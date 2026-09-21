import os
import re


def extract_domains(content):

    match = re.search(
        r"server_name\s+([^;]+);",
        content
    )

    if not match:
        return []

    return match.group(1).split()



def extract_proxy_container(content):

    match = re.search(
        r"proxy_pass\s+http://([^:/\s]+)",
        content
    )

    if not match:
        return None

    return match.group(1)



def parse_nginx_file(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        content = f.read()


    return {

        "config": os.path.basename(path),

        "domains":
            extract_domains(content),

        "container":
            extract_proxy_container(content)

    }



def scan_nginx_configs(config_path):

    results = []


    if not os.path.isdir(config_path):

        return results



    for filename in os.listdir(config_path):

        if filename.endswith(".conf"):

            full_path = os.path.join(
                config_path,
                filename
            )


            results.append(
                parse_nginx_file(full_path)
            )


    return results
