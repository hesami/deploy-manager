import os

from core.app_inspector import inspect_app
from core.registry import (
    upsert_application,
    add_domain,
    add_source,
    add_database,
)


def import_app(app_path, nginx_path):

    result = inspect_app(
        app_path,
        nginx_path
    )


    app = result["application"]

    container = result.get("container")


    app_data = {

        "name": app["name"],

        "path": app["path"],

        "type": app["type"],

        "container_name":
            container.get("name")
            if container else None,

        "image_name":
            container.get("image")
            if container else None,

        "compose_file":
            result.get("compose_file"),

        "docker_network":
            result.get("docker_network", []),

        "status":
            result.get("status")
    }


    app_id = upsert_application(
        app_data
    )


    if result.get("nginx"):

        add_domain(
            app_id,
            result["nginx"]
        )


    add_source(
        app_id,
        result.get("source")
    )


    add_database(
        app_id,
        result.get("database")
    )


    return app_id



def import_all(apps_path, nginx_path):

    imported = []


    for name in os.listdir(apps_path):

        app_path = os.path.join(
            apps_path,
            name
        )


        if not os.path.isdir(app_path):

            continue


        app_id = import_app(
            app_path,
            nginx_path
        )


        imported.append(
            {
                "name": name,
                "id": app_id
            }
        )


    return imported
