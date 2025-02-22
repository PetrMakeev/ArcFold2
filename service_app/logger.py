import logging
import os
from datetime import datetime, timedelta
import yaml
import multiprocessing

def load_config():
    """Загружает конфигурацию из файла config.yaml."""
    try:
        with open("config.yaml", "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        return {}

# Глобальная переменная для хранения логгера
_logger_instance = None

class RotatingDailyLogger:
    """Класс для создания логов с ежедневным переключением файлов."""
    def __init__(self, log_dir="logs", retention_days=15, console_mode="visible"):
        self.log_dir = log_dir
        self.retention_days = retention_days
        self.console_mode = console_mode.lower() == "visible"
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_date = None
        self.logger = None
        self._initialize_logger()

    def _initialize_logger(self):
        """Инициализирует логгер с именем файла, соответствующим текущей дате."""
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"logs_{self.current_date}.log")

        # Настройка логгера
        self.logger = logging.getLogger("TaskLogger")
        if not self.logger.hasHandlers():  # Проверяем, добавлены ли обработчики
            self.logger.setLevel(logging.INFO)

            # Обработчик для записи в файл
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            self.logger.addHandler(file_handler)

            # Обработчик для вывода в консоль (если включено)
            if self.console_mode:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
                self.logger.addHandler(console_handler)

            # Сообщение об инициализации логгера только в основном процессе
            if multiprocessing.current_process().name == "MainProcess":
                self.logger.info(f"Logger initialized for {self.current_date}.")

    def log(self, level, message):
        """Проверяет дату и записывает сообщение в текущий файл лога, с выводом в консоль при необходимости."""
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self.current_date:
            self._initialize_logger()  # Смена файла лога при смене суток
        log_method = getattr(self.logger, level.lower(), None)
        if log_method:
            log_method(message)

    def clean_old_logs(self):
        """Удаляет устаревшие логи."""
        retention_date = datetime.now() - timedelta(days=self.retention_days)
        try:
            for log_file in os.listdir(self.log_dir):
                file_path = os.path.join(self.log_dir, log_file)
                if os.path.isfile(file_path) and log_file.startswith("logs_"):
                    try:
                        date_part = log_file[5:15]  # Извлекаем YYYY-MM-DD из имени файла
                        log_date = datetime.strptime(date_part, "%Y-%m-%d")
                        if log_date < retention_date:
                            os.remove(file_path)
                            print(f"Deleted old log file: {file_path}")
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Error while cleaning old logs: {e}")


def setup_logger():
    """Функция для создания или получения единственного экземпляра логгера."""
    global _logger_instance
    if _logger_instance is None:
        config = load_config()  # Подгружаем настройки из конфигурации
        log_retention_days = config.get("log_retention_days", 15)
        console_mode = config.get("console_mode", "visible")
        _logger_instance = RotatingDailyLogger(retention_days=log_retention_days, console_mode=console_mode)
        _logger_instance.clean_old_logs()
    return _logger_instance
