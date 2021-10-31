import time
import logging


def profile(function):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = function(*args, **kwargs)
        t2 = time.time()
        logging.debug(f"{function.__name__} execution time is {t2 - t1}")
        return result

    return wrapper
