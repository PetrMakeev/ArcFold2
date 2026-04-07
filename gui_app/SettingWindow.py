from PySide6.QtWidgets import (
    QMainWindow,
    QTableView, 
    QMenu, QMessageBox, QFileDialog
)
from PySide6 import (
    QtCore, 
    QtGui, 
    QtWidgets
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QCursor, QAction, QIcon, QFont
from datetime import datetime
from os import path, getcwd, remove
import subprocess
import psutil
import sys
import os
from datetime import datetime, timedelta

from gui_app.ui_setting import Ui_frmSetting

days_translation = {
    "Monday": "ПН",
    "Tuesday": "ВТ",
    "Wednesday": "СР",
    "Thursday": "ЧТ",
    "Friday": "ПТ",
    "Saturday": "СБ",
    "Sunday": "ВС"
}

day_mapping = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
}

class SettingWindow(QMainWindow, Ui_frmSetting):
    def __init__(self, parent=None, *args, obj=None, **kwargs):
        super(SettingWindow, self).__init__(parent, *args, **kwargs) 
        self.setupUi(self)
        
        self.parent = parent
        
        self.status_service = False
       
        self.setting_ui_element()
        

    # подготовка к редактированию настроек
    def read_config(self, config):
        self(config.get('temp_directory', path.dirname(path.abspath(__file__))+"\\temp_archiver"))
        self.edit_log_retention_days.setValue(config.get('log_retention_days', 1))
        

    def check_task_exists(self, task_name):
        """Проверяет, существует ли задача с указанным именем в планировщике задач."""
        try:
            result = subprocess.run(['schtasks', '/Query', '/TN', task_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False

    def update_button_service(self):
        """Обновляет текст кнопки в зависимости от статуса задачи."""
        self.status_service = self.check_task_exists("ArcFoldServiceStart")
        
        if self.status_service:
            self.btn_set_schedule.setText("Удалить службу")
        else:
            self.btn_set_schedule.setText("Установить службу")


    def add_task(self):
        if getattr(sys, 'frozen', False):  # Проверяем, запущено ли в скомпилированном виде
            path_app = sys.executable  # Путь к .exe файлу
        else:
            path_app = path.abspath(__file__)  # Путь к .py файлу (если запускается в интерпретаторе)

        
        """Добавляет задачу в планировщик задач с наивысшими правами и скрытым режимом."""
        task_name = "ArcFoldServiceStart"
        program_path = path.dirname(path_app) + "\\ArcFoldService.exe"  # Укажите правильный путь к программе
        username = self.edit_login.text()
        password = self.edit_password.text()
        working_directory = path.dirname(path_app)
        
        # Команда для создания задачи
        command = (
            f'schtasks /Create /TN {task_name} /TR "{program_path}" /SC MINUTE /MO 1 '
            f'/RU {username} /RP "{password}" /RL HIGHEST /F /NP '
        )

        # PowerShell-команда для изменения рабочей директории
        ps_command = f"""
            $task = Get-ScheduledTask -TaskName "{task_name}"
            $task.Actions[0].WorkingDirectory = "{working_directory}"
            Set-ScheduledTask -TaskName "{task_name}" -Action $task.Actions[0]
            """
            
        # Запускаем PowerShell в скрытом режиме
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # Отключаем окно            
            
        try:
            # Выполнение команды
            subprocess.run(command, shell=True, check=True)
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                check=True, capture_output=True, text=True, startupinfo=startupinfo
            )
            print("Задача успешно добавлена в планировщик.")
            QMessageBox.information(self, "Успех!", f"Служба добавлена в планировщик для автозапуска")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при добавлении задачи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении службы в автозапуск: {e}")
                
    def delete_task(self):
        """Удаляет задачу из планировщика задач и завершает связанные процессы."""
        task_name = "ArcFoldServiceStart"
        
        # Удаление задачи из планировщика
        command = f'schtasks /Delete /TN {task_name} /F'
        subprocess.run(command, shell=True)
        
        # Поиск и завершение процессов ArcFoldService
        processes_to_kill = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Проверяем имя процесса
                if proc.info['name'] == "ArcFoldService.exe":
                    processes_to_kill.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Проверяем, что найдено ровно 2 процесса
        error_kill = None
        if len(processes_to_kill) == 2:
            for proc in processes_to_kill:
                try:
                    proc.kill()  # Завершаем процесс
                    print(f"Процесс {proc.info['pid']} завершен.")
                except Exception as e:
                    print(f"Ошибка при завершении процесса {proc.info['pid']}: {e}")
                    error_kill = True

            if not error_kill:
                QMessageBox.information(self, "Успех!", f"Служба удалена из планировщика")
        
                
        else:
            print(f"Найдено {len(processes_to_kill)} процессов ArcFoldService.exe. Ожидалось 2.")
        
            
    def toggle_task(self):
        """Переключает состояние задачи в планировщике."""
        if self.status_service:
            self.delete_task()
        else:
            if self.edit_login.text() == "" or self.edit_password.text() == "":
                QMessageBox.critical(self, "Ошибка", f"Не указаны данные логин и пароль для создания задачи")

            self.add_task()
        self.status_service = not self.status_service
        self.update_button_service()



    # сохранение задачи
    def save_setting(self):
        self.parent.save_setting(self.edit_temp_directory.text(), self.edit_log_retention_days.value())
        self.hide()


    # диалог выбора папки     
    def select_folder(self, title = "Выберите папку", initial_directory= ""):
        folder_path = QFileDialog.getExistingDirectory(self, title, initial_directory)
        if folder_path:
            folder_path = path.normpath(folder_path)  # Преобразуем слеши
            self.edit_temp_directory.setText(folder_path)
        pass  
    

    ##############################################################################
    # Настройка интерфейса
    #############################################################################
    def setting_ui_element(self):

        self.update_button_service()
        self.btn_set_schedule.clicked.connect(self.toggle_task)
        # Проверка наличия задачи в планировщике
        
       # привязка кнопки отмена и сохранения
        self.btn_cancel.clicked.connect(self.hide)
        self.btn_save.clicked.connect(self.save_setting)

        self.btn_temp_directory.clicked.connect(lambda: self.select_folder("Выберите папку для временных файлов...", self.edit_temp_directory.text()))
        


    ##############################################################################
    # Абстрактная модель данные
    #  поля  ["Название", "Периодичность", "Время" ]
    #############################################################################
class TaskTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, columns):
        super().__init__()
        self._data = data
        self._columns = columns

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # return f"Column {section + 1}"
                return str(self._columns[section])
            elif orientation == Qt.Orientation.Vertical:
                return str(section + 1)  # Номера строк
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter  # Центрирование заголовко
        
        
    def data(self, index, role):
        if not index.isValid():
            return None
        
        if role == Qt.ItemDataRole.DisplayRole:
            
            # Получаем исходное значение
            value = self._data[index.row()][index.column()]

            #  поля  ["Название", "Периодичность", "Время" ]
             
            if index.column() == 1:
                if value == "daily":
                    time = self._data[index.row()][3]
                    return f"Ежедневно в {time}"
                elif value  == "weekly":
                    days = ""
                    list_days = self._data[index.row()][4]
                    # list_days = list_days[0].split(",")
                    time = self._data[index.row()][3]
                    if list_days:
                        for eld in list_days:
                            days = days + (", " if not days=="" else "") + days_translation.get(eld.strip())
                    return f"Еженедельно в {time} по {days}"
                elif value == "monthly":
                    list_days = self._data[index.row()][5]
                    time = self._data[index.row()][3]
                    return f"Ежемесячно в {time}: {", ".join(map(str, list_days))}"
            else:
                return self._data[index.row()][index.column()]
            
        if role == QtCore.Qt.ItemDataRole.TextAlignmentRole and (index.column() == 2  ):
            return QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignVCenter
        # if role == QtCore.Qt.ItemDataRole.TextAlignmentRole and (index.column() in [1, 2] ):
        #     return QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter
        

        # Изменение толщины шрифта по условию в строке
        if role == Qt.ItemDataRole.FontRole:
            active = self._data[index.row()][6] 
            
            if active:
                font = QFont()
                font.setBold(True)  # Жирный шрифт
                return font

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        if not self._data:
            return 0
        return len(self._data[0])    
    
    

class ButtonManager:
    def __init__(self, ui_elements):
        """
        Инициализирует менеджер фильтров.
        :param ui_elements: Словарь с элементам UI.
        """
        self.ui_elements = ui_elements

    def toggle_button(self, ui_name, is_checked):
        """
        Включает или выключает фильтр и обновляет UI.
        :param ui_name: Название кнопки.
        :param is_checked: Состояние кнопки (True/False).
        """

        # Обновление стиля кнопки
        font = QFont('Arial', 10)
        font.setBold(is_checked)
        button = self.ui_elements[ui_name]
        button.setFont(font)
        
        if ui_name == "btn_direct_to_archive":
            if not is_checked:
                button.setText("Копировать напрямую в архив")
            else:
                button.setText("Копировать через временную папку")

    # def reset_buttons(self):
    #     """
    #     Сбрасывает все фильтры.
    #     """
    #     for filter_name in self.filters.keys():
    #         self.toggle_filter(filter_name, False)
    

    
    
    
    
def next_run_time(task):
    """
    Вычисляет следующее время запуска задачи по данным из конфигурации.

    :param task: Словарь с параметрами задачи, включая расписание.
                 Формат задачи:
                 {
                     "schedule": "daily" | "weekly" | "monthly" ,
                     "time": "HH:MM",
                     "days": [1, 15, 30],  # Только для monthly
                     "day_of_week": ["Monday", "Sunday"],  # Только для weekly
                 }
    :return: Объект datetime с указанием следующего времени запуска.
    """
    now = datetime.now()

    # Тип расписания
    schedule_type = task["schedule"]

    if schedule_type == "daily":
        # Ежедневное расписание
        task_time = datetime.strptime(task["time"], "%H:%M").time()
        next_run = datetime.combine(now.date(), task_time)

        if next_run <= now:
            # Если текущее время уже прошло, добавляем один день
            next_run += timedelta(days=1)

    elif schedule_type == "weekly":
        # Еженедельное расписание
        day_of_week_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
        task_time = datetime.strptime(task["time"], "%H:%M").time()
        
        list_days = [item.strip() for item in task.get("days_of_week")]
        
        task_days = [day_of_week_map[day.lower()] for day in list_days]

        # Ищем ближайший день недели
        today_weekday = now.weekday()
        days_until_next = [(day - today_weekday) % 7 for day in task_days]
        min_days_until_next = min(days_until_next)
        next_run_date = now.date() + timedelta(days=min_days_until_next)

        next_run = datetime.combine(next_run_date, task_time)

    elif schedule_type == "monthly":
        # Ежемесячное расписание
        task_time = datetime.strptime(task["time"], "%H:%M").time()
        task_days = task["days_of_month"]

        # Проверяем текущий месяц
        current_month = now.month
        current_year = now.year

        # Сортируем дни месяца
        task_days = sorted(task_days)

        for day in task_days:
            try:
                next_run_date = datetime(current_year, current_month, day)
                next_run = datetime.combine(next_run_date, task_time)
                if next_run > now:
                    break
            except ValueError:
                # Пропускаем некорректные дни (например, 30 февраля)
                continue
        else:
            # Если нет подходящих дней в текущем месяце, переходим на следующий
            next_month = (current_month % 12) + 1
            next_year = current_year + (1 if next_month == 1 else 0)
            next_run_date = datetime(next_year, next_month, task_days[0])
            next_run = datetime.combine(next_run_date, task_time)

    elif schedule_type == "one_time":
        # Одноразовое расписание
        next_run = datetime.strptime(task["datetime"], "%Y-%m-%d %H:%M:%S")

        if next_run <= now:
            next_run = None  # Задача уже прошла

    else:
        raise ValueError(f"Unsupported schedule type: {schedule_type}")

    return next_run    

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