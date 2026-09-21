import sys
import threading
import time


STAGES = {
    "PREFLIGHT": 10,
    "BACKUP": 10,
    "BUILD": 35,
    "TAG": 10,
    "DEPLOY": 20,
    "HEALTH": 10,
    "COMMIT": 5
}


SPINNER = [
    "⠋",
    "⠙",
    "⠹",
    "⠸",
    "⠼",
    "⠴",
    "⠦",
    "⠧",
    "⠇",
    "⠏"
]


class ProgressManager:

    def __init__(self):

        self.completed = []
        self.current = None
        self.running = False
        self.index = 0
        self.thread = None


    def percent(self):

        total = 0

        for stage in self.completed:
            total += STAGES.get(stage,0)

        return total


    def start(self, stage, message=""):

        self.current = stage
        self.running = True


        def animate():

            while self.running:

                spinner = SPINNER[
                    self.index % len(SPINNER)
                ]

                self.index += 1


                percent = self.percent()


                line = (
                    f"\r{spinner} {stage:<12} {message} "
                    f"[{percent}%]"
                )


                sys.stdout.write(line)
                sys.stdout.flush()

                time.sleep(0.1)


        self.thread = threading.Thread(
            target=animate,
            daemon=True
        )

        self.thread.start()


    def complete(self, stage):

        self.running = False

        if self.thread:
            self.thread.join(
                timeout=0.2
            )


        if stage not in self.completed:
            self.completed.append(stage)


        print(
            "\r" + (" " * 80),
            end="\r"
        )

        print(
            f"✓ {stage:<12} completed"
        )


    def fail(self, stage, message):

        self.running = False

        print(
            f"\r✗ {stage:<12} {message}"
        )
