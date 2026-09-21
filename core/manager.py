import os
import shutil
from datetime import datetime

from core.docker_reader import run_command, run_command_stream
from core.health import check_container
from core.console import Console
from core.output import Output
from core.registry import (
    add_deployment,
    get_application_by_path,
    update_deployment_status,
    get_previous_rebuild,
    update_deployment_full,
    add_image_version,
    deactivate_image_versions,
    add_backup,
    get_backups,
    get_last_backup
)


def get_logs(container_name, lines=100):

    return run_command(
        f"docker logs --tail {lines} {container_name}"
    )



def restart_container(container_name):

    return run_command(
        f"docker restart {container_name}"
    )



def backup_env(path):

    env_file = os.path.join(
        path,
        ".env"
    )


    if not os.path.isfile(env_file):

        return "No .env file found"


    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )


    backup_file = (
        f"{env_file}.backup-{timestamp}"
    )


    shutil.copy2(
        env_file,
        backup_file
    )


    return backup_file




def get_running_container_image(path):

    import subprocess
    import json

    result = subprocess.run(
        f"cd {path} && docker compose ps -q",
        shell=True,
        text=True,
        capture_output=True
    )

    container_id = result.stdout.strip()

    if not container_id:
        return None

    inspect = subprocess.run(
        f"docker inspect {container_id}",
        shell=True,
        text=True,
        capture_output=True
    )

    if inspect.stdout:
        data = json.loads(inspect.stdout)[0]
        return data.get('Config', {}).get('Image')

    return None


def rebuild_project(path):

    app_name = os.path.basename(path)

    app_record = get_application_by_path(path)

    app_id = app_record[0] if app_record else None

    deployment_id = None

    try:

        Console.step("BACKUP")
        Console.info("Creating environment backup...")

        env_backup = backup_env(path)

        print(
            env_backup,
            "\n",
            flush=True
        )


        image_before = get_running_container_image(path)


        deployment_id = add_deployment(
            app_id=app_id,
            action="rebuild",
            status="running",
            image_before=image_before,
            env_backup=env_backup,
            message=f"Rebuild started for {app_name}"
        )


        print(
            "Building image...\n",
            flush=True
        )


        run_command_stream(
            f"cd {path} && docker compose build",
            show_progress=True
        )


        Output.success(
            "Image built successfully"
        )


        current_image = get_running_container_image(path)

        image_tag = generate_image_tag()

        repository = current_image.split(":")[0]


        versioned_image = tag_image(
            current_image,
            repository,
            image_tag
        )


        deactivate_image_versions(
            app_id
        )


        add_image_version(
            app_id,
            repository,
            image_tag,
            versioned_image,
            "active"
        )


        write_image_override(
            path,
            versioned_image
        )


        print(
            f"Image version: {versioned_image}",
            flush=True
        )


        run_command_stream(
            f"cd {path} && docker compose up -d --no-build",
            show_progress=False
        )


        import subprocess

        result = subprocess.run(
            f"cd {path} && docker compose ps -q",
            shell=True,
            text=True,
            capture_output=True
        )

        container_id = result.stdout.strip()
        container_name = None

        if container_id:

            import json

            inspect = subprocess.run(
                f"docker inspect {container_id}",
                shell=True,
                text=True,
                capture_output=True
            )

            if inspect.stdout:
                data = json.loads(inspect.stdout)[0]
                container_name = data.get("Name", "").replace("/", "")


        if container_name and not wait_container_ready(container_name):

            write_image_override(
                path,
                image_before
            )

            run_command_stream(
                f"cd {path} && docker compose up -d --no-build",
                show_progress=False
            )

            update_deployment_status(
                deployment_id,
                "failed",
                "Health check failed. Automatic rollback completed",
                image_after=image_before
            )

            return "Automatic rollback completed"


        update_deployment_status(
            deployment_id,
            "success",
            f"Rebuild completed for {app_name}",
            image_after=versioned_image
        )


        Console.success(
            "Rebuild completed"
        )

        return ""


    except Exception as e:


        if deployment_id:

            update_deployment_status(
                deployment_id,
                "failed",
                str(e)
            )


        Console.error(
            f"Rebuild failed: {e}"
        )


        return ""



def wait_container_ready(container_name, attempts=5):

    import time

    stable_checks = 0


    for _ in range(attempts):

        health = check_container(
            container_name
        )


        if not health.get("running"):

            stable_checks = 0

            time.sleep(3)

            continue


        if health.get("restart_count", 0) != 0:

            stable_checks = 0

            time.sleep(3)

            continue


        docker_health = health.get(
            "healthy"
        )


        if docker_health not in (
            None,
            "none",
            "healthy"
        ):

            stable_checks = 0

            time.sleep(3)

            continue


        stable_checks += 1


        if stable_checks >= 2:

            return True


        time.sleep(3)


    return False


def get_project_image(path):

    import subprocess

    result = subprocess.run(
        f"cd {path} && docker compose config --images",
        shell=True,
        text=True,
        capture_output=True
    )

    if result.stdout.strip():

        return result.stdout.strip().splitlines()[0]


    return None


def rollback_project(path, target_version=None):

    app_record = get_application_by_path(path)

    if not app_record:

        return "Application not found"


    app_id = app_record[0]


    last = None

    if not target_version:

        last = get_previous_rebuild(
            app_id
        )


    if not target_version and not last:

        return "No successful deployment found"


    if target_version:

        target_image = target_version

    else:

        target_image = last[7]


    old_env_backup = last[8] if not target_version else None

    current_env_backup = backup_env(path)
    current_image = get_running_container_image(path)


    deployment_id = add_deployment(
        app_id=app_id,
        action="rollback",
        status="running",
        image_before=current_image,
        env_backup=current_env_backup,
        message=f"Rollback started for {os.path.basename(path)}"
    )


    try:

        if old_env_backup and os.path.isfile(old_env_backup):

            shutil.copy2(
                old_env_backup,
                os.path.join(
                    path,
                    ".env"
                )
            )


        if target_image:

            write_image_override(
                path,
                target_image
            )


        run_command_stream(
            f"cd {path} && docker compose up -d --no-build",
            show_progress=False
        )


        image_after = get_project_image(path)


        update_deployment_full(
            deployment_id,
            "success",
            f"Rollback completed for {os.path.basename(path)}",
            image_after=image_after
        )


        return "Rollback completed"


    except Exception as e:

        update_deployment_full(
            deployment_id,
            "failed",
            str(e)
        )

        return f"Rollback failed: {e}"




def create_project_backup(path, app_id):

    import os
    import shutil

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    backup_dir = os.path.join(
        "/opt/deploy-manager/registry/backups",
        os.path.basename(path),
        timestamp
    )

    os.makedirs(
        backup_dir,
        exist_ok=True
    )

    files = [
        ".env",
        "docker-compose.yml",
        "docker-compose.override.yml"
    ]

    for file_name in files:

        source = os.path.join(
            path,
            file_name
        )

        if os.path.isfile(source):

            shutil.copy2(
                source,
                backup_dir
            )

    add_backup(
        app_id,
        "project",
        backup_dir
    )

    return backup_dir



def restore_project_backup(path, backup_path):

    import os
    import shutil

    if not os.path.isdir(backup_path):
        return False

    for file_name in [
        ".env",
        "docker-compose.yml",
        "docker-compose.override.yml"
    ]:

        source = os.path.join(
            backup_path,
            file_name
        )

        target = os.path.join(
            path,
            file_name
        )

        if os.path.isfile(source):

            shutil.copy2(
                source,
                target
            )

    return True





def cleanup_images(images):

    results = []

    for image in images:

        full_image = image[1]

        result = run_command(
            f"docker rmi {full_image}"
        )


        success = (
            "Error" not in result
            and
            "error" not in result.lower()
        )


        results.append(
            (
                full_image,
                success,
                result
            )
        )


    return results



def generate_image_tag():

    return datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )



def tag_image(image_name, repository, tag):

    run_command(
        f"docker tag {image_name} {repository}:{tag}"
    )

    return f"{repository}:{tag}"



def write_image_override(path, image_name):

    override_path = os.path.join(
        path,
        "docker-compose.override.yml"
    )

    content = f"""services:
  app:
    image: {image_name}
"""

    with open(
        override_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(content)

    return override_path
