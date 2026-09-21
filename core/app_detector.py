import os


def detect_app(path):

    result = {
        "name": os.path.basename(path),
        "path": path,
        "type": "unknown",
        "docker": False,
        "compose": False,
        "prisma": False,
    }


    if os.path.isfile(
        os.path.join(path, "docker-compose.yml")
    ):
        result["compose"] = True


    if os.path.isfile(
        os.path.join(path, "Dockerfile")
    ):
        result["docker"] = True


    if (
        os.path.isfile(
            os.path.join(path, "next.config.js")
        )
        or
        os.path.isfile(
            os.path.join(path, "next.config.ts")
        )
    ):
        result["type"] = "nextjs"


    elif os.path.isfile(
        os.path.join(path, "package.json")
    ):
        result["type"] = "node"


    elif os.path.isfile(
        os.path.join(path, "index.html")
    ):
        result["type"] = "static"


    if os.path.isfile(
        os.path.join(path, "prisma", "schema.prisma")
    ):
        result["prisma"] = True


    return result



def scan_apps(apps_path):

    apps = []


    if not os.path.isdir(apps_path):
        return apps


    for name in os.listdir(apps_path):

        path = os.path.join(
            apps_path,
            name
        )


        if os.path.isdir(path):

            apps.append(
                detect_app(path)
            )


    return apps
