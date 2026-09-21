import os


class UI:

    CYAN = "\033[96m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    RESET = "\033[0m"



def clear_screen():

    os.system("clear")



def pause():

    input(
        "\nPress Enter to continue..."
    )



def header(text):

    print(
        f"""
{UI.CYAN}╔══════════════════════════════╗
║ {text:^28} ║
╚══════════════════════════════╝{UI.RESET}
"""
    )



def menu_item(number, text, *args):

    print(
        f"{UI.GREEN}{number}){UI.RESET} {text}"
    )



def line():

    print(
        f"{UI.CYAN}{'─'*30}{UI.RESET}"
    )



def success(message):

    print(
        f"{UI.GREEN}✓ {message}{UI.RESET}"
    )



def warning(message):

    print(
        f"{UI.YELLOW}! {message}{UI.RESET}"
    )



def error(message):

    print(
        f"{UI.RED}✗ {message}{UI.RESET}"
    )



def info(message):

    print(
        f"{UI.BLUE}{message}{UI.RESET}"
    )


def section(title):

    print(
        f"""
{UI.CYAN}{title}
{'─'*30}{UI.RESET}
"""
    )


def value(label, data):

    print(
        f"{UI.WHITE}{label:<20}{UI.RESET}: {data}"
    )
