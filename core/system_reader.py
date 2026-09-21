import subprocess


def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    except Exception as e:
        return str(e)


def get_os_info():
    return run_command("cat /etc/os-release | grep PRETTY_NAME")


def get_docker_version():
    return run_command("docker --version")


def get_compose_version():
    return run_command("docker compose version")


def get_docker_networks():
    return run_command("docker network ls --format '{{.Name}}'")


def get_running_containers():
    return run_command(
        "docker ps --format '{{.Names}}'"
    )
