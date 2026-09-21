class Console:

    RESET = "\033[0m"

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


    @staticmethod
    def info(message):

        print(
            f"{Console.BLUE}[INFO]{Console.RESET} {message}",
            flush=True
        )


    @staticmethod
    def success(message):

        print(
            f"{Console.GREEN}✓ {message}{Console.RESET}",
            flush=True
        )


    @staticmethod
    def warning(message):

        print(
            f"{Console.YELLOW}! {message}{Console.RESET}",
            flush=True
        )


    @staticmethod
    def error(message):

        print(
            f"{Console.RED}✗ {message}{Console.RESET}",
            flush=True
        )


    @staticmethod
    def step(message):

        print(
            f"{Console.CYAN}[{message}]{Console.RESET}",
            flush=True
        )
