# archiver.py
import os
import zipfile
from datetime import datetime
from service_app.logger import setup_logger
import fnmatch
import multiprocessing


import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from service_app.logger import setup_logger
import threading

logger = setup_logger()


def parse_mask(mask):
    """
    Разбирает строку масок в список.

    :param mask: строка масок, разделённая запятой, либо None
    :return: список масок или пустой список
    """
    if mask == "":
        return []
    return [m.strip() for m in mask.split(",")]


def validate_files(source, exclude_masks=[], include_masks=[]):

    # exclude_masks = parse_mask(exclude_masks)
    # include_masks = parse_mask(include_masks)

    if not os.path.exists(source):
        logger.log("error", f"Source path does not exist: {source}")
        return False

    if os.path.isfile(source):
        return True

    # files = os.listdir(source)
    # matched_files = []
    
    # for root, _, files in os.walk(source):
    #     for file in files:
    #         file_path = os.path.join(root, file)
    #         include_match = any(fnmatch.fnmatch(file, mask) for mask in include_masks) if include_masks else True
    #         exclude_match = any(fnmatch.fnmatch(file, mask) for mask in exclude_masks) if exclude_masks else False

    #         if include_match and not exclude_match:
    #             matched_files.append(file_path)

    # if not matched_files:
    #     logger.log("warning", f"No matching files found in {source}")
    #     return False

    return True

def create_archive(task_name, 
                   source, 
                   destination, 
                   exclude_masks=[], 
                   include_masks=[], 
                   temp_directory=None, 
                   direct_to_archive=False, 
                   compression="zip_stored",
                   name1c=None,
                   dbname=None,
                   loginwin=False,
                   login1c=None):
    """
    Создает архив с указанными параметрами.
    
    :param task_name: Имя задачи.
    :param source: Исходный путь.
    :param destination: Путь для сохранения архива.
    :param exclude_mask: Маска исключаемых файлов.
    :param include_mask: Маска включаемых файлов.
    :param temp_directory: Временная директория.
    :param direct_to_archive: Использовать ли временную папку.
    :param compression: Тип сжатия ("zip_stored" или "zip_deflated").
    :param name1c: имя сервера 1c SQL
    :param dbname: имя базы данных 1с
    :param loginwin: авторизация windows (True False)
    :param login1c: пароль SQL
    
    """
    # exclude_masks = parse_mask(exclude_masks)
    # include_masks = parse_mask(include_masks)
    
    try:
        
        # Настройка типа сжатия
        zip_compression = zipfile.ZIP_DEFLATED if compression == "zip_deflated" else zipfile.ZIP_STORED

        # Проверяем и создаем директорию для хранения архива, если она  не существует
        if not os.path.exists(destination):
            os.makedirs(destination)

        # Проверяем и создаем временную директорию, если и не существует
        if not os.path.exists(temp_directory):
            os.makedirs(temp_directory)


        archive_name = f"{task_name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
        archive_path = os.path.join(destination, archive_name)

        print(archive_name)
        print(archive_path)
        
        with zipfile.ZipFile(archive_path, 'w', compression=zip_compression) as archive:
            for root, _, files in os.walk(source):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, source)

                  
                    if include_masks == []:
                        include_match = True
                    else:
                        include_match = any(fnmatch.fnmatch(file, mask) for mask in include_masks) if include_masks else True
                    if exclude_masks == []:
                        exclude_match = False
                    else:
                        exclude_match = any(fnmatch.fnmatch(file, mask) for mask in exclude_masks) if exclude_masks else False

                    if include_match and not exclude_match:
                        # Определяем путь для добавления в архив
                        path_to_add = file_path
                        
                        # Проверяем, можно ли прочитать файл
                        try:
                            with open(file_path, 'rb'):
                                pass  # Если удалось открыть, значит, файл не заблокирован
                        except (IOError, OSError) as e:
                            # Если не удалось открыть, файл, скорее всего, заблокирован
                            # Копируем его во временную директорию
                            if temp_directory:
                                temp_file_path = os.path.join(temp_directory, os.path.basename(file_path))
                                
                                # Чтобы избежать конфликта имен при совпадении имен файлов
                                # в разных поддиректориях, можно сохранить относительный путь
                                # или использовать уникальные имена. Для простоты здесь
                                # используется basename, но можно усложнить при необходимости.
                                
                                # Пробуем скопировать файл
                                try:
                                    # Импортируем shutil в начале файла, если еще не импортирован
                                    import shutil
                                    
                                    # Копируем файл во временную директорию
                                    shutil.copy2(file_path, temp_file_path)
                                    
                                    # Теперь работаем с копией
                                    path_to_add = temp_file_path
                                    print(f"Файл {file_path} был заблокирован. Используется копия из {temp_file_path}")
                                except Exception as copy_error:
                                    print(f"Не удалось скопировать заблокированный файл {file_path}: {copy_error}")
                                    continue  # Пропускаем этот файл
                            else:
                                # Если временная директория не задана, пропускаем заблокированный файл
                                print(f"Файл {file_path} заблокирован, но временная директория не указана. Пропуск.")
                                continue
                            
                        
                        # Добавляем файл (оригинал или копию) в архив
                        archive.write(path_to_add, rel_path)

        logger.log("info", f"Archive created at: {archive_path}")
        return archive_path

    except Exception as e:
        logger.log("error", f"Error creating archive: {e}")
        return None

def run_archive_in_process(task_name, source, destination, exclude_mask=[], include_mask=[], temp_directory=None, direct_to_archive=False, compression="zip_stored"):
    """
    Запускает процесс архивирования в отдельном процессе.

    :param task_name: Имя задачи архивирования.
    :param source: Исходный путь для архивирования.
    :param destination: Путь сохранения архива.
    :param exclude_mask: Маска исключаемых файлов.
    :param include_mask: Маска включаемых файлов.
    :param temp_directory: Временная папка.
    :param direct_to_archive: Указывает, использовать ли временную папку.
    :param compression: Тип сжатия ("zip_stored" или "zip_deflated").
    """
    process = multiprocessing.Process(
        target=create_archive,
        args=(task_name, source, destination, exclude_mask, include_mask, temp_directory, direct_to_archive, compression)
    )
    process.start()
    logger.log("info", f"Archiving process started with PID {process.pid} for task '{task_name}'")
    return process




#############################
#   конфигурация
#############################
# console_mode - отображение консоли: "visible" - показывать, "hidden" - скрывать
# log_retention_days - хранение логов в днях 
# temp_directory - временная папка для архивировния
# параметры task
  # name - имя задачи
    # schedule - режим запуска: "monthly" - ежемесячно, "weekly" - еженедельно,  "daily" - ежедневно
    # days_of_month - дни запуска в течении месяца: [1, 15, 28] - список чисел месяца 
    # days_of_week - дни запуска в течении недели:  ["Sunday"] - список дней недели
    # time - время запуска задачи
    # source - источник архивирования
    # destination - место сохранения архива
    # exclude_mask - список масок файлов исплючаемых из архивирования: ["*.log"]  
    # include_mask - список масок файлов включаемых в архив: ["*.docx"] 
    # direct_to_archive - архивирование в архив: "true" - прямое, "false" - через временную папку  
    # compression - сжатие архива: "zip_deflated" - сжатие zip, "zip_stored" - без сжатия
    # keep_last - количество хранимых последних версий архива 

last_reload_time = 0
reload_lock = threading.Lock()

logger = setup_logger()

class ConfigFileEventHandler(FileSystemEventHandler):
    def __init__(self, config_path, reload_callback):
        self.config_path = config_path
        self.reload_callback = reload_callback

    def on_modified(self, event):
        if event.src_path == self.config_path:
            logger.log("info", f"Configuration file {self.config_path} modified. Reloading...")
            self.reload_callback()

def watch_config(config_path, reload_callback):
    """Отслеживает изменения файла конфигурации и вызывает функцию перезагрузки."""
    class ConfigFileEventHandler(FileSystemEventHandler):
        def on_modified(self, event):
            global last_reload_time
            if event.src_path == config_path:
                with reload_lock:
                    current_time = time.time()
                    # Убедимся, что вызов reload_config происходит не чаще чем раз в 1 секунду
                    if current_time - last_reload_time > 1:
                        logger.log("info", f"Configuration file {config_path} modified. Reloading...")
                        reload_callback()
                        last_reload_time = current_time

    event_handler = ConfigFileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(config_path), recursive=False)
    observer.start()
    return observer

