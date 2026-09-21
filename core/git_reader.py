import os
import subprocess


def run_git_command(path, command):

    try:

        result = subprocess.run(
            command,
            cwd=path,
            shell=True,
            text=True,
            capture_output=True
        )

        return result.stdout.strip()

    except Exception:

        return ""



def is_git_repository(path):

    return os.path.isdir(
        os.path.join(path, ".git")
    )



def get_remote(path):

    return run_git_command(
        path,
        "git remote get-url origin"
    )



def get_branch(path):

    branch = run_git_command(
        path,
        "git branch --show-current"
    )

    return branch



def detect_git_source(path):

    result = {
        "type": "local",
        "method": None,
        "remote": None,
        "branch": None
    }


    if not is_git_repository(path):

        return result



    remote = get_remote(path)


    result["type"] = "git"
    result["remote"] = remote
    result["branch"] = get_branch(path)


    if remote.startswith("git@"):

        result["method"] = "ssh"


    elif remote.startswith("http"):

        result["method"] = "https"


    return result
