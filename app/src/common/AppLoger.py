import os
from datetime import datetime
from django.conf import settings

LOG_FILE_PATH = os.path.join(settings.PATH_LOGS, "app.log")


def check_file(file_path=LOG_FILE_PATH):
    """
    Verifica y crea el archivo de log si no existe
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w"):
                pass
        return True
    except IOError as e:
        print(f"Error al crear el archivo: {e}")
        return False


def _logging_message(message, file_path=LOG_FILE_PATH):
    """
    Registra un mensaje normal en el archivo especificado
    """
    check_file(file_path)
    with open(file_path, "a") as file:
        file.write(f"[{datetime.now()}] [MESSAGE] {message}\n")


def _logging_error(message, file_path=LOG_FILE_PATH):
    """
    Registra un mensaje de error en el archivo especificado
    """
    check_file(file_path)
    with open(file_path, "a") as file:
        file.write(f"[{datetime.now()}] [ERROR]: {message}\n")


def loggin_event(message, error=False, file_path=LOG_FILE_PATH):
    """
    Registra un evento en el archivo de log
    
    Args:
        message (str): Mensaje a registrar
        error (bool): Si es True, se registra como error
        file_path (str): Ruta del archivo donde registrar
    """
    if error:
        _logging_error(message, file_path)
    else:
        _logging_message(message, file_path)

    return True


def log_access(message):
    """
    Registra específicamente eventos de acceso a la aplicación
    
    Args:
        message (str): Mensaje de acceso a registrar
    """
    return loggin_event(f"ACCESO - {message}", error=False)


def log_access_error(message):
    """
    Registra específicamente errores de acceso a la aplicación
    
    Args:
        message (str): Mensaje de error de acceso a registrar
    """
    return loggin_event(f"ACCESO ERROR - {message}", error=True)
