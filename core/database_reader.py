import os
import re
from urllib.parse import urlparse


def read_env_file(path):

    env = {}

    if not os.path.isfile(path):

        return env


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()


            if not line or line.startswith("#"):

                continue


            if "=" in line:

                key, value = line.split(
                    "=",
                    1
                )

                env[key.strip()] = value.strip()


    return env



def parse_database_url(url):

    if not url:

        return None


    parsed = urlparse(url)


    return {

        "engine":
            parsed.scheme,

        "host":
            parsed.hostname,

        "database":
            parsed.path.lstrip("/"),

        "username":
            parsed.username

    }



def detect_database(app_path):

    env_path = os.path.join(
        app_path,
        ".env"
    )


    env = read_env_file(env_path)


    database_url = (
        env.get("DATABASE_URL")
    )


    return parse_database_url(
        database_url
    )
