

from core.manager import (
    backup_env,
    get_running_container_image,
    generate_image_tag,
    tag_image,
    write_image_override,
    wait_container_ready
)

from core.docker_reader import (
    run_command_stream
)


from core.registry import (
    add_deployment,
    deactivate_image_versions,
    add_image_version,
    update_deployment_status
)



from core.preflight import run_preflight

from core.progress import ProgressManager


from core.preflight import run_preflight



from enum import Enum


class DeployState(Enum):

    INIT = "INIT"

    BACKUP = "BACKUP"

    BUILD = "BUILD"

    TAG = "TAG"

    DEPLOY = "DEPLOY"

    HEALTH = "HEALTH"

    COMMIT = "COMMIT"

    ROLLBACK = "ROLLBACK"

    SUCCESS = "SUCCESS"

    FAILED = "FAILED"



class DeployPipeline:


    def __init__(self, name, path, app_id):

        self.name = name

        self.path = path

        self.app_id = app_id

        self.image_before = None

        self.image_after = None

        self.deployment_id = None

        self.env_backup = None

        self.state = DeployState.INIT

        self.progress = ProgressManager()













    def get_container_name(self):

        import subprocess
        import json


        result = subprocess.run(
            f"cd {self.path} && docker compose ps -q",
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

            data = json.loads(
                inspect.stdout
            )[0]


            return data.get(
                "Name",
                ""
            ).replace(
                "/",
                ""
            )


        return None







    def rollback_stage(self):

        self.transition(
            DeployState.ROLLBACK
        )


        if not self.image_before:

            self.transition(
                DeployState.FAILED
            )

            return False


        write_image_override(
            self.path,
            self.image_before
        )


        run_command_stream(
            f"cd {self.path} && docker compose up -d --no-build",
            show_progress=False
        )


        if self.deployment_id:

            update_deployment_status(
                self.deployment_id,
                "failed",
                "Health check failed. Automatic rollback completed",
                image_after=self.image_before
            )


        self.transition(
            DeployState.FAILED
        )


        return True



    def commit_stage(self):

        self.progress.start(
            "COMMIT",
            "Saving deployment record"
        )


        self.transition(
            DeployState.COMMIT
        )


        if not self.image_after:

            self.transition(
                DeployState.FAILED
            )

            return False


        repository, tag = self.image_after.split(":")


        deactivate_image_versions(
            self.app_id
        )


        add_image_version(
            self.app_id,
            repository,
            tag,
            self.image_after,
            "active"
        )


        if self.deployment_id:

            update_deployment_status(
                self.deployment_id,
                "success",
                f"Deploy completed for {self.name}",
                image_after=self.image_after
            )


        self.progress.complete(
            "COMMIT"
        )


        self.transition(
            DeployState.SUCCESS
        )


        return True



    def health_stage(self):

        self.progress.start(
            "HEALTH",
            "Checking stability"
        )


        self.transition(
            DeployState.HEALTH
        )


        container = self.get_container_name()


        if not container:

            self.progress.fail(
                "HEALTH",
                "Container not found"
            )


            self.transition(
                DeployState.ROLLBACK
            )

            return False



        if not wait_container_ready(container):

            self.progress.fail(
                "HEALTH",
                "Container not stable"
            )


            self.transition(
                DeployState.ROLLBACK
            )

            return False



        self.progress.complete(
            "HEALTH"
        )


        self.transition(
            DeployState.COMMIT
        )


        return True



    def deploy_stage(self):

        self.progress.start(
            "DEPLOY",
            "Restarting container"
        )


        self.transition(
            DeployState.DEPLOY
        )


        if not self.image_after:

            self.transition(
                DeployState.FAILED
            )

            return False


        write_image_override(
            self.path,
            self.image_after
        )


        result = run_command_stream(
            f"cd {self.path} && docker compose up -d --no-build",
            show_progress=False
        )


        if result is False:

            self.progress.fail(
                "DEPLOY",
                "Container deployment failed"
            )


            self.transition(
                DeployState.FAILED
            )

            return False


        self.progress.complete(
            "DEPLOY"
        )


        self.transition(
            DeployState.HEALTH
        )


        return True



    def tag_stage(self):

        self.progress.start(
            "TAG",
            "Creating image version"
        )


        self.transition(
            DeployState.TAG
        )


        current_image = get_running_container_image(
            self.path
        )


        if not current_image:

            self.transition(
                DeployState.FAILED
            )

            return False


        image_tag = generate_image_tag()


        repository = current_image.split(":")[0]


        versioned_image = tag_image(
            current_image,
            repository,
            image_tag
        )


        self.image_after = versioned_image


        self.progress.complete(
            "TAG"
        )


        self.transition(
            DeployState.DEPLOY
        )


        return True



    def build_stage(self):

        self.progress.start(
            "BUILD",
            "Building docker image"
        )


        self.transition(
            DeployState.BUILD
        )


        result = run_command_stream(
            f"cd {self.path} && docker compose build",
            show_progress=False
        )


        if result is False:

            self.progress.fail(
                "BUILD",
                "Docker build failed"
            )


            self.transition(
                DeployState.FAILED
            )

            return False


        self.progress.complete(
            "BUILD"
        )


        self.transition(
            DeployState.TAG
        )


        return True




    def preflight_stage(self):

        self.progress.start(
            "PREFLIGHT",
            "Running checks"
        )


        checks = run_preflight(
            self.path
        )


        failed = [
            name
            for name, result in checks.items()
            if not result
        ]


        self.preflight_error = None


        if failed:

            self.preflight_error = (
                "Preflight failed: "
                +
                ",".join(failed)
            )


            self.transition(
                DeployState.FAILED
            )

            return False


        self.progress.complete(
            "PREFLIGHT"
        )


        self.transition(
            DeployState.BACKUP
        )


        return True


    def backup_stage(self):

        self.progress.start(
            "BACKUP",
            "Creating backup"
        )


        self.transition(
            DeployState.BACKUP
        )


        self.env_backup = backup_env(
            self.path
        )


        self.image_before = get_running_container_image(
            self.path
        )


        self.deployment_id = add_deployment(
            app_id=self.app_id,
            action="deploy",
            status="running",
            image_before=self.image_before,
            env_backup=self.env_backup,
            message=f"Deploy started for {self.name}"
        )


        self.progress.complete(
            "BACKUP"
        )


        self.transition(
            DeployState.BUILD
        )


        return True



    def transition(self, state):

        self.state = state


    def status(self):

        return self.state.value









def run_pipeline(name, path, app_id):

    pipeline = DeployPipeline(
        name,
        path,
        app_id
    )


    try:


        pipeline.deployment_id = add_deployment(
            app_id=app_id,
            action="deploy",
            status="running",
            message=f"Deployment started for {name}"
        )


        if not pipeline.preflight_stage():

            update_deployment_status(
                pipeline.deployment_id,
                "failed",
                pipeline.preflight_error
                or
                "Preflight checks failed"
            )

            return pipeline


        if not pipeline.backup_stage():
            return pipeline


        if not pipeline.build_stage():
            return pipeline


        if not pipeline.tag_stage():
            return pipeline


        if not pipeline.deploy_stage():
            pipeline.rollback_stage()
            return pipeline


        if not pipeline.health_stage():
            pipeline.rollback_stage()
            return pipeline


        pipeline.commit_stage()


        return pipeline



    except Exception as e:


        if pipeline.state in (
            DeployState.DEPLOY,
            DeployState.HEALTH
        ):

            pipeline.rollback_stage()


        else:

            pipeline.transition(
                DeployState.FAILED
            )


        return pipeline


