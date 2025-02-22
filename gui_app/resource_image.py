import os
import sys

def resource_path(relative_path: str) -> str:
    """
    Возвращает абсолютный путь к ресурсам.
    Работает как при запуске из .py файлов, так и из .exe файла.
    
    :param relative_path: Относительный путь к ресурсу
    :return: Абсолютный путь
    """
    try:
        # PyInstaller упаковывает временные файлы в _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # В режиме разработки используем текущую директорию
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
