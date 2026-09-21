import os

from core.app_detector import detect_app
from core.git_reader import detect_git_source
from core.nginx_reader import scan_nginx_configs
from core.database_reader import detect_database
from core.docker_reader import (
    get_containers,
    get_container_networks
)


def find_container_for_app(app_name):

    containers = get_containers()

    candidates = []


    for container in containers:

        name = container.get("Names", "")
        image = container.get("Image", "")


        if (
            app_name in name
            or
            app_name in image
        ):

            candidates.append(
                {
                    "name": name,
                    "image": image,
                    "status": container.get("Status"),
                    "ports": container.get("Ports")
                }
            )


    if candidates:
        return candidates[0]


    return None



def find_nginx_for_container(container_name, nginx_path):

    configs = scan_nginx_configs(
        nginx_path
    )


    for config in configs:

        if config.get("container") == container_name:

            return config


    return None



def inspect_app(app_path, nginx_path):

    result = {}


    app = detect_app(
        app_path
    )

    result["application"] = app


    result["source"] = detect_git_source(
        app_path
    )


    result["database"] = detect_database(
        app_path
    )


    container = find_container_for_app(
        app["name"]
    )

    result["container"] = container


    if container:

        result["nginx"] = find_nginx_for_container(
            container["name"],
            nginx_path
        )

        result["status"] = "running"


        result["docker_network"] = get_container_networks(
            container["name"]
        )


    else:

        result["nginx"] = None
        result["status"] = "not_running"
        result["docker_network"] = []



    compose_file = os.path.join(
        app_path,
        "docker-compose.yml"
    )


    if os.path.isfile(compose_file):

        result["compose_file"] = compose_file

    else:

        result["compose_file"] = None


    return result
