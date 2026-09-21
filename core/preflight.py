import os
import shutil
import subprocess


def check_docker():

    result = subprocess.run(
        "docker info",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0



def check_disk(path):

    usage = shutil.disk_usage(path)

    free_gb = usage.free / (1024**3)

    return free_gb >= 2



def check_compose(path):

    result = subprocess.run(
        f"cd {path} && docker compose config",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0



def run_preflight(path):

    checks = {
        "docker": check_docker(),
        "disk": check_disk(path),
        "compose": check_compose(path)
    }


    return checks
