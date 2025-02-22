# config_watcher.py
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from service_app.logger import setup_logger
import threading

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