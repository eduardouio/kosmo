import os
from datetime import datetime
from django.conf import settings

LOG_FILE_PATH = os.path.join(settings.PATH_LOGS, "app.log")


def check_file():
    try:
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        if not os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "w") as file:
                pass
        return True
    except IOError as e:
        print(f"Error al crear el archivo: {e}")
        return False


def _logging_message(message):
    check_file()
    with open(LOG_FILE_PATH, "a") as file:
        file.write(f"[{datetime.now()}] [MESSAGE] {message}\n")


def _logging_error(message):
    check_file()
    with open(LOG_FILE_PATH, "a") as file:
        file.write(f"[{datetime.now()}] [ERROR]: {message}\n")


def loggin_event(message, error=False):
    if error:
        _logging_error(message)
    else:
        _logging_message(message)

    return True
