import sqlite3

from core.docker_reader import get_container_details


DB_PATH = "/opt/deploy-manager/registry/deploy-manager.db"



def get_app_status(name):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()


    cursor.execute("""
    SELECT
        id,
        name,
        type,
        path,
        container_name,
        image_name,
        status
    FROM applications
    WHERE name=?
    """,
    (name,))


    row = cursor.fetchone()

    conn.close()


    if not row:
        return None


    result = {

        "id": row[0],
        "name": row[1],
        "type": row[2],
        "path": row[3],
        "container": row[4],
        "image": row[5],
        "registry_status": row[6]

    }


    if row[4]:

        docker = get_container_details(
            row[4]
        )


        if docker:

            result["docker_status"] = (
                docker
                .get("State", {})
                .get("Status")
            )

            result["docker_running"] = (
                docker
                .get("State", {})
                .get("Running")
            )


    return result
