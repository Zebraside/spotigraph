import time
import logging


def profile(function, mark_start=False):
    def wrapper(*args, **kwargs):
        if mark_start:
            print(f"Starting {function.__name__}...")
        t1 = time.time()
        result = function(*args, **kwargs)
        t2 = time.time()
        print(f"{function.__name__} execution time is {t2 - t1}")
        return result

    return wrapper
