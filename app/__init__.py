import django.db.backends.utils
from django.db import OperationalError
import time


django_execute_wrapper = django.db.backends.utils.CursorWrapper.execute


def execute_wrapper(*args, **kwargs):
    print("I am here!")
    for attempt in range(3):
        try:
            return django_execute_wrapper(*args, **kwargs)
        except OperationalError as error:
            error_code = error.args[0]
            if error_code != 1213 or attempt == 2:
                raise error
            time.sleep(0.2)


django.db.backends.utils.CursorWrapper.execute = execute_wrapper
