
from PyQt6.QtWidgets import (QMainWindow,
                             QTableView, 
                             QMenu, QMessageBox, QFileDialog)
from PyQt6 import (QtCore, 
                   QtGui, 
                   QtWidgets)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QCursor, QAction, QIcon
from datetime import datetime
from os import path, getcwd, remove
import subprocess
import psutil
import sys
from gui_app.resource_image import resource_path
from gui_app.ui_setting import Ui_frmSetting

class SettingWindow(QMainWindow, Ui_frmSetting):
    def __init__(self, parent=None, *args, obj=None, **kwargs):
        super(SettingWindow, self).__init__(parent, *args, **kwargs) 
        self.setupUi(self)
        
        self.parent = parent
        
        self.status_service = False
        
       
        self.setting_ui_element()
        
        


    # подготовка к редактированию настроек
    def read_config(self, config):
        self.edit_temp_directory.setText(config.get('temp_directory', path.dirname(path.abspath(__file__))+"\\temp_archiver"))
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
        

