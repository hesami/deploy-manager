import json

from core.docker_reader import get_container_details



def check_container(container_name):

    result = {
        "container": container_name,
        "running": False,
        "status": None,
        "restart_count": None,
        "healthy": None
    }


    container = get_container_details(
        container_name
    )


    if not container:
        return result


    state = container.get(
        "State",
        {}
    )


    result["status"] = state.get(
        "Status"
    )


    result["running"] = state.get(
        "Running",
        False
    )


    result["restart_count"] = container.get(
        "RestartCount"
    )


    if "Health" in state:

        result["healthy"] = (
            state["Health"]
            .get("Status")
        )

    else:

        result["healthy"] = "none"


    return result
