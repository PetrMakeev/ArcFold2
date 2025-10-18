from multiprocessing import freeze_support
import schedule
import time
from datetime import datetime
import yaml
from threading import Thread
import os
import ctypes
import sys
import shutil

from service_app.logger import setup_logger
from service_app.db_handler import init_db, log_task_status
from service_app.archiver import run_archive_in_process, validate_files, watch_config


logger = setup_logger()


APP_NAME = "ArcFoldService"  # Название для записи в реестре
MUTEX_NAME = "Global\\ArcFoldServiceInstanceMutex"  # Уникальный мьютекс

config = None
tasks = []

def get_executable_path():
    """
    Определяет путь к исполняемому файлу.
    В режиме скрипта возвращает путь к service.py, в режиме .exe — путь к .exe файлу.
    """
    if getattr(sys, 'frozen', False):  # Если запущен как .exe (pyinstaller)
        return sys.executable
    return os.path.abspath(sys.argv[0])


        
def load_config():
    """Загружает конфигурацию из файла config.yaml."""
    try:
        with open('config.yaml', 'r', encoding="utf-8") as file:
            config = yaml.safe_load(file)
        logger.log("info", "Configuration file loaded successfully.")
        return config
    except Exception as e:
        logger.log("error", f"Error loading configuration file: {e}")
        sys.exit(1)

def hide_console():
    """Скрывает консольное окно."""
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        user32.ShowWindow(hWnd, 0)  # 0 - скрыть окно
        

def schedule_task(task, temp_directory):
    if task['schedule'] == 'daily':
        schedule.every().day.at(task['time']).do(run_task, task, temp_directory)
    elif task['schedule'] == 'weekly':
        # Используем отдельный метод для проверки дней недели
        schedule.every().day.at(task['time']).do(run_weekly_task, task, temp_directory)
    elif task['schedule'] == 'monthly':
        # Используем отдельный метод для проверки дней месяца
        schedule.every().day.at(task['time']).do(run_monthly_task, task, temp_directory)
    elif task['schedule'] == 'once':
        run_task(task, temp_directory)

def run_weekly_task(task, temp_directory):
    """Запускает задачу, если текущий день недели совпадает с указанным в настройках."""
    today = datetime.now().strftime("%A")
    days_of_week = task.get('days_of_week', [])
    if today in days_of_week:
        logger.log("info", f"Running weekly task {task['name']} on day {today}")
        run_task(task,temp_directory)
    else:
        logger.log("info", f"Skipping weekly task {task['name']}, not scheduled for today.")
    
    
def run_monthly_task(task, temp_directory):
    """Запускает задачу, если текущий день месяца совпадает с указанным в настройках."""
    today = datetime.now().day
    days_of_month = task.get('days_of_month', [])
    if today in days_of_month:
        logger.log("info", f"Running monthly task {task['name']} on day {today}")
        run_task(task, temp_directory)
    else:
        logger.log("info", f"Skipping monthly task {task['name']}, not scheduled for today.")

def run_task(task, temp_directory):
    if not task.get('active', True):
        logger.log("info", f"Skipping weekly task {task['name']} as not active" )
        return
    logger.log("info", f"Running task {task['name']} at {datetime.now()}")

    # Проверка на наличие только одного типа маски
    exclude_mask = task.get('exclude_mask')
    include_mask = task.get('include_mask')
    if exclude_mask and include_mask:
        logger.log("error", f"Task {task['name']} has both 'exclude_mask' and 'include_mask'. Only one can be specified.")
        return

    if validate_files(task['source'], exclude_mask, include_mask):
        archive_path = run_archive_in_process(
            task_name=task['name'],
            source=task['source'],
            destination=task['destination'],
            exclude_mask=exclude_mask,
            include_mask=include_mask,
            temp_directory=temp_directory,
            direct_to_archive=task.get('direct_to_archive', False,),
            compression = task.get('compression', "zip_deflated")
        )
        # удаляем временную папку 
        if os.path.exists(temp_directory):
            shutil.rmtree(temp_directory)
            
        if archive_path:
            logger.log("info",f"Task {task['name']} completed successfully.")
            log_task_status(task['name'], "success")  # Запись успешного выполнения в базу данных
        else:
            logger.log("error",f"Task {task['name']} failed.")
            log_task_status(task['name'], "failure")  # Запись ошибки в базу данных
    else:
        logger.log("error", f"Validation failed for task {task['name']}.")
        log_task_status(task['name'], "failure")
        

def reload_config():
    global tasks
    logger.log("info","Reloading configuration and rescheduling tasks.")
    config = load_config()
    if config:
        schedule.clear()  # Очищаем расписание задач
        tasks = config.get('tasks', [])
        temp_directory = config.get('temp_directory', os.path.dirname(os.path.abspath(__file__))+"\\temp_archiver")
        for task in tasks:
            schedule_task(task, temp_directory)

def start_service():
    # Инициализация базы данных
    init_db()
    
    config = load_config()  # Загружаем конфигурацию
    
    # проверяем источники в задачах
    config = check_source_directory(config)
    
    # Проверка режима консоли
    console_mode = config.get("console_mode", "visible").lower()
    if console_mode == "hidden":
        logger.log("info", "Switching to hidden console mode.")
        hide_console()
    
    temp_directory = config.get('temp_directory', os.path.dirname(os.path.abspath(__file__))+"\\temp_archiver")
    for task in config['tasks']:
        task_temp_directory = os.path.join(temp_directory, task.get('name'))
        schedule_task(task, task_temp_directory)

    # Мониторинг изменений файла конфигурации
    config_path = os.path.abspath('config.yaml')
    watch_thread = Thread(target=watch_config, args=(config_path, reload_config), daemon=True)
    watch_thread.start()

    logger.log("info", "Service started. Waiting for scheduled tasks...")
    while True:
        schedule.run_pending()
        time.sleep(1)


def create_temp_directory(task_name, temp_directory):
    """Создает временную директорию для задачи."""
    task_temp_dir = os.path.join(temp_directory, task_name)
    os.makedirs(task_temp_dir, exist_ok=True)
    logger.log("info", f"Temporary directory created for task '{task_name}': {task_temp_dir}")
    return task_temp_dir

def is_another_instance_running():
    """Проверяет, запущен ли уже экземпляр приложения."""
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    last_error = kernel32.GetLastError()

    if last_error == 183:  # ERROR_ALREADY_EXISTS
        logger.log("warning", "Another instance of the application is already running. Exiting.")
        sys.exit(0)  # Завершаем текущий процесс

def check_source_directory(config):
    change_active_tasks = False
    for id_task, task in enumerate(config['tasks']):
        have_source = os.path.isdir(task.get("source", "None"))
        if not have_source and task['active']:
            task['active'] = False
            change_active_tasks = True
        # elif have_source and not task['active']:
        #     task['active'] = True
        #     change_active_tasks = True
            
    if change_active_tasks:
        # Сохраняем обновленный файл
        with open('config.yaml', "w", encoding="utf-8") as file:
            yaml.dump(config, file, allow_unicode=True, default_flow_style=None, indent=3)        
    return config    
        
def main():
    freeze_support()  # Для предотвращения повторной инициализации на Windows
    is_another_instance_running()  # Контроль запуска одной копии
    start_service()        
