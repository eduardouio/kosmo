import os
from datetime import datetime
from django.conf import settings

LOG_FILE_PATH = os.path.join(settings.BASE_DIR, 'static', 'logs', 'log.txt')


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


def logging_message(message):
    check_file()
    with open(LOG_FILE_PATH, "a") as file:
        file.write(f"[{datetime.now()}] -> MESSAGE {message}\n")


def logging_error(message):
    check_file()
    with open(LOG_FILE_PATH, "a") as file:
        file.write(f"[{datetime.now()}] -> ERROR: {message}\n")
