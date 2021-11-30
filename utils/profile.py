import time
import logging


class Performer:
    def __init__(self, tag: str = ""):
        self.start_time = time.time()
        self.loop_time = self.start_time

        self.tag = tag

        logging.debug(f"Start measuring {tag}")

    def restart(self):
        self.start_time = time.time()
        self.loop_time = self.start_time

    def section(self, section_tag):
        current_time = time.time()
        logging.debug(
            f"{self.tag}:{section_tag}: Section time: {current_time - self.loop_time}")

        self.loop_time = current_time

    def elapsed(self):
        current_time = time.time()
        logging.debug(
            f"{self.tag}: Total time: {current_time - self.start_time}")


def profile(function, mark_start=False):
    def wrapper(*args, **kwargs):
        if mark_start:
            print(f"Starting {function.__name__}...")
        t1 = time.time()
        result = function(*args, **kwargs)
        t2 = time.time()
        # print(f"{function.__name__} execution time is {t2 - t1}")
        return result

    return wrapper
