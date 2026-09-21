import sys


class Output:

    RESET = "\033[0m"
    BLUE = "\033[96m"
    GREEN = "\033[92m"
    RED = "\033[91m"


    @staticmethod
    def stage(name):

        print(
            f"\n{Output.BLUE}[{name}]{Output.RESET}\n",
            flush=True
        )


    @staticmethod
    def info(message):

        print(
            f"{Output.BLUE}ℹ {message}{Output.RESET}",
            flush=True
        )


    @staticmethod
    def success(message):

        print(
            f"{Output.GREEN}✓ {message}{Output.RESET}",
            flush=True
        )


    @staticmethod
    def error(message):

        print(
            f"{Output.RED}✗ {message}{Output.RESET}",
            flush=True
        )


    @staticmethod
    def progress(percent):

        width = 30

        filled = int(
            width * percent / 100
        )

        bar = (
            "█" * filled +
            "░" * (width - filled)
        )

        sys.stdout.write(
            "\r"
            + " " * 80
            + "\r"
        )

        sys.stdout.write(
            f"{Output.BLUE}Progress:{Output.RESET} {bar} {percent}%"
        )

        sys.stdout.flush()


    @staticmethod
    def progress_finish():

        sys.stdout.write("\n")
        sys.stdout.flush()
