import subprocess
import json


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



def run_command_stream(command, show_progress=False):

    try:

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )


        if process.stdout:

            for line in process.stdout:

                # Output is intentionally consumed silently.
                # Pipeline ProgressManager handles CLI progress.
                _ = line


        process.wait()


        if process.returncode != 0:

            return False


        return True


    except Exception:

        return False



def get_containers():

    output = run_command(
        "docker ps --format '{{json .}}'"
    )

    containers = []


    for line in output.splitlines():

        if line.strip():

            containers.append(
                json.loads(line)
            )


    return containers



def get_container_details(name):

    output = run_command(
        f"docker inspect {name}"
    )

    if output:

        return json.loads(output)[0]


    return None



def get_networks():

    output = run_command(
        "docker network ls --format '{{json .}}'"
    )

    networks = []


    for line in output.splitlines():

        if line.strip():

            networks.append(
                json.loads(line)
            )


    return networks



def get_container_networks(name):

    output = run_command(
        f"docker inspect {name}"
    )


    if not output:

        return []


    try:

        data = json.loads(output)[0]

        networks = (
            data
            .get("NetworkSettings", {})
            .get("Networks", {})
        )


        return list(
            networks.keys()
        )


    except Exception:

        return []
