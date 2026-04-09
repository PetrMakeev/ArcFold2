from PySide6.QtWidgets import (
    QMainWindow,
    QTableView, 
    QMenu,
    QComboBox, QMessageBox, QFileDialog, QLabel
)
from PySide6 import (
    QtCore, 
    QtGui, 
    QtWidgets
)
from PySide6.QtCore import Qt, QDate, QSize, QRegularExpression, QTime, QTimer
from PySide6.QtGui import QCursor, QFont, QAction, QIcon, QRegularExpressionValidator, QPainter, QPixmap, QColor
from datetime import datetime
import os
from ruamel.yaml import YAML
from gui_app.ui_main import Ui_MainWindow
from gui_app.SettingWindow import SettingWindow, ButtonManager, TaskTableModel, next_run_time, resource_path, days_translation, day_mapping

from service_app.service import load_config, check_source_directory
from service_app.password_encoder import PasswordEncoder

allowed_chars = set("1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZабвгдежзийклмнопрстуфхчшщьыъэюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЧШЩЬЫЪЭЮЯ,. *")
allowed_chars_name = set("1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZабвгдежзийклмнопрстуфхчшщьыъэюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЧШЩЬЫЪЭЮЯ-_ ")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        
        self.setWindowIcon(QIcon(resource_path("icons\\archive.ico")))

        #подключаем энкодер паролей
        self.encoder = PasswordEncoder()

         # Создаем объект YAML (лучше сделать это один раз, возможно, как атрибут класса,
        # но для простоты идентично предыдущему поведению помещаем тут)
        self.yaml = YAML()
        self.yaml.allow_unicode = True
        self.yaml.default_flow_style = None
        # Устанавливаем отступы для вложенных структур (аналог indent=3 в pyyaml)
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        
        # создаем формы приказов и подразделений
        self.w_setting = SettingWindow(parent = self)
        
        # считываем настройки
        self.data = self.load_config()
        self.curr_name_task =  None
        self.curr_include_mask = []
        self.curr_exclude_mask = []
        self.mode_edit = None
        self.curr_task_id = None
        
        # скрываем закладки панелей таб
        for i in range(self.tab_period.count()):
            self.tab_period.setTabVisible(i, False)
        
        # настройка интерфейса
        self.setting_ui_element()
        
        # обновляем таблицу
        self.refresh_grid()
        self.table.selectRow(0)


    ##############################################################################
    # функционал формы
    #############################################################################
    # настройка вызова контекстного меню
    def contextMenuEvent(self, point):
        # проверяем чтобы был клик в области строк грида
        if  (type(point) == QtCore.QPoint):
            context_menu = QMenu(self)
           
            pop_add = QAction(QIcon(resource_path("icons\\add.png")), "Новая задача", self)
            context_menu.addAction(pop_add)
            pop_add.triggered.connect(self.popup_add)
            
            # если нет записей в гриде отключаем пункты меню
            if self.data:
                pop_edit = QAction(QIcon(resource_path("icons\\edit.png")), "Изменить задачу", self)
                context_menu.addAction(pop_edit)
                pop_edit.triggered.connect(self.popup_edit)
                
                pop_del = QAction(QIcon(resource_path("icons\\del.png")), "Удалить задачу", self)
                context_menu.addAction(pop_del)
                pop_del.triggered.connect(self.popup_del)
                
            context_menu.addSeparator()
            

            pop_setting = QAction(QIcon(resource_path("icons\\install.png")), "Настройки", self)
            pop_setting.triggered.connect(self.popup_setting)
            context_menu.addAction(pop_setting)
                
            context_menu.popup(QCursor.pos())


    # пункт меню удалить
    def popup_del(self):
        confirmation_dialog = QMessageBox(self)
        confirmation_dialog.setIcon(QMessageBox.Icon.Warning)
        confirmation_dialog.setWindowTitle("Подтверждение")
        confirmation_dialog.setText("Вы уверены, что хотите удалить задачу?")
        confirmation_dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirmation_dialog.setDefaultButton(QMessageBox.StandardButton.No)

        # Получение ответа пользователя
        user_response = confirmation_dialog.exec()

        if user_response == QMessageBox.StandardButton.Yes:
            self.curr_task_id = self.table.currentIndex().row()
            
            # получаем название задачи
            name_task = self.data[self.curr_task_id][0]

            # Фильтруем список tasks, оставляя только те, которые не совпадают с указанным именем
            self.config["tasks"] = [task for task in self.config["tasks"] if task["name"] != name_task]

            # Сохраняем обновленный файл
            with open('config.yaml', "w", encoding="utf-8") as file:
                self.yaml.dump(self.config, file)

            self.data = self.load_config()
            self.refresh_grid()

    # пункт настройки
    def popup_setting(self):
        self.w_setting.read_config(self.config)
        self.w_setting.update_button_service()
        self.w_setting.show()
        

    # пункт меню Добавить
    def popup_add(self):
        # показываем панель грида
        self.frm_edit.setVisible(True)
        self.frm_grid.setVisible(False)  
        
        self.mode_edit = "ADD"
        self.curr_task_id = None
         
        self.curr_name_task = ""
        self.edit_name.setText(self.curr_name_task)
        self.edit_source.setText("")
        self.edit_destination.setText("")
        self.edit_period.setCurrentIndex(0)
        self.tab_period.setCurrentIndex(0)
        self.edit_time.setTime(QTime(0, 0))
        self.set_days_of_week(False)
        self.set_days_of_month(False)
        self.curr_include_mask = []
        self.edit_mask_incl.setText("")
        self.curr_exclude_mask = []
        self.edit_mask_excl.setText("")
        self.edit_keep_last.setValue(1)
        self.edit_compression.setCurrentIndex(0)
        if self.btn_direct_to_archive.isChecked():
            self.btn_direct_to_archive.click()
        self.edit_name1c.setText("")
        self.edit_dbname.setText("")
        self.chk_loginwin.setCheckState(Qt.Checked) 
        self.edit_login1c.setEnabled(False)
        self.lbl_login1c.setEnabled(False)
        self.edit_login1c.setText("")
        self.tab_object.setCurrentIndex(0)
            
    # пункт меню Изменить     
    def popup_edit(self):
        # показываем панель грида
        self.frm_edit.setVisible(True)
        self.frm_grid.setVisible(False)  
        
        self.mode_edit = "EDIT"
        self.curr_task_id = self.table.currentIndex().row()
         
        # получаем данные о задаче
        task = self.config.get("tasks")[self.curr_task_id]
        # заполняем форму 
        self.curr_name_task = task.get("name", "")
        self.edit_name.setText(self.curr_name_task)
        if self.btn_active.isChecked() != task.get("active", True):
            self.btn_active.click()
        self.edit_source.setText(task.get("source", ""))
        self.edit_destination.setText(task.get("destination", ""))
        period = 2 if task.get("schedule", "daily") == "monthly" else 1 if task.get("schedule", "daily") == "weekly" else 0 
        self.edit_period.setCurrentIndex(period)
        self.tab_period.setCurrentIndex(period)
        time = task.get("time", "00:00")
        self.edit_time.setTime(QTime(int(time[:2]), int(time[3:])))
        self.set_days_of_week(False) 
        if period == 1:       
            self.read_days_of_week(task.get("days_of_week", []))
        self.set_days_of_month(False)
        if period == 2:
            self.read_days_of_month(task.get("days_of_month",[]))
        self.curr_include_mask = task.get("include_mask", [])
        self.edit_mask_incl.setText(", ".join(self.curr_include_mask) if len(self.curr_include_mask)>0 else "") 
        self.curr_exclude_mask = task.get("exclude_mask", [])
        self.edit_mask_excl.setText(", ".join(self.curr_exclude_mask) if len(self.curr_exclude_mask)>0 else "") 
        self.edit_keep_last.setValue(task.get("keep_last", 5))
        compression = task.get("compression", "zip_stored")
        self.edit_compression.setCurrentIndex(0 if compression == "zip_stored" else 1)
        if self.btn_direct_to_archive.isChecked():
            self.btn_direct_to_archive.click()
        if task.get("direct_to_archive", True):
            self.btn_direct_to_archive.click()
        self.edit_name1c.setText(task.get("name1с", ""))
        self.edit_dbname.setText(task.get("dbname", ""))
        if task.get("loginwin", True) == True:
            #loginwin = Qt.Checked
            self.edit_login1c.setEnabled(False)
            self.lbl_login1c.setEnabled(False)
            self.chk_loginwin.setChecked(True)
        else:
            #loginwin = Qt.unChecked
            self.edit_login1c.setEnabled(True)
            self.lbl_login1c.setEnabled(True)
            self.chk_loginwin.setChecked(False) 
        login1c = task.get("login1c", "")
        if not login1c == "":
            login1c = self.encoder.decode(login1c)
        self.edit_login1c.setText(login1c)
        self.tab_object.setCurrentIndex(0)
        


    # проверка введенных масок
    def mask_check(self, type_mask, silent = False):
        if type_mask == "include":
            verify_mask = self.edit_mask_incl.text()
        elif type_mask == "exclude":
            verify_mask = self.edit_mask_excl.text()
        else:
            return False
        if  verify_mask == "":
            return True
        # получаем список масок
        try:
            if not set(verify_mask).issubset(allowed_chars):
                raise ValueError("Использование в маске файлов недопустимых символов!")  # Генерируем ошибку
            if "," in verify_mask:
                verify_mask = [el.strip() for el in verify_mask.split(",") if el.strip() != "" ]
            else:
                verify_mask =[verify_mask.strip(),]


            if type_mask == "include":
                self.curr_include_mask = verify_mask
            elif type_mask == "exclude":
                self.curr_exclude_mask = verify_mask
            if not silent:
                QMessageBox.information(self, "Успешно", f"Маска распознана.")
    
            return True
        except:
            QMessageBox.critical(self, "Ошибка", f"Маска не распознана. Повторите ввод")
            if type_mask == "include":
                self.edit_mask_incl.setFocus()
            if type_mask == "exclude":
                self.edit_mask_excl.setFocus()
            return False
                

                            
    # настраиваем грид
    def refresh_grid(self):
        column_titles = ["Название задачи", "Периодичность", "След. запуск", "", "", "", ""]
        self.model = TaskTableModel(self.data, column_titles)

        self.table.setModel(self.model)
        
        # ширина столбцов
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 380)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 0)
        self.table.setColumnWidth(4, 0)
        self.table.setColumnWidth(5, 0)
        self.table.setColumnWidth(6, 0)
  
        self.table.verticalHeader().setFixedWidth(20) 
           
        # режим выделения = строка целиком
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)  
        self.model.layoutChanged.emit()  


    #  загрузка настроек
    def load_config(self):
        data = []
        self.config = load_config()
        
        # проверяем источники в задачах
        self.config = check_source_directory(self.config)
        
        # получаем общие параметры
        self.log_retention_days = self.config.get("log_retention_days", 10)
        self.temp_directory = self.config.get('temp_directory', os.path.dirname(os.path.abspath(__file__))+"\\temp_archiver")
        app_path = os.path.dirname(self.temp_directory)
        if not os.path.exists(app_path):
            self.temp_directory =  os.path.dirname(os.path.abspath(__file__)) + "\\temp_archiver" 
        self.config["temp_directory"] = self.temp_directory
        # Сохраняем изменения о временной папке в конфигурационный файл
        with open('config.yaml', "w", encoding="utf-8") as file:
            self.yaml.dump(self.config, file)
        
        # формируем таблицу для грида
        for el in self.config.get('tasks',[]):
            next_start_task = next_run_time(el)
            data.append([
                el.get('name'), 
                el.get('schedule'), 
                datetime.strftime(next_start_task, "%d.%m.%Y %H:%M"),
                el.get('time') ,
                el.get('days_of_week', []),
                el.get('days_of_month', []),
                el.get('active', True)
                ])
        return data
    

    # отмена сохранения
    def not_save(self):
        # показываем панель грида
        self.frm_edit.setVisible(False)
        self.frm_grid.setVisible(True)
        
        
    # сохранение задачи
    def save_task(self):
        # проверяем данные перед сохранением      
        if not set(self.edit_name.text()).issubset(allowed_chars_name): 
            QMessageBox.critical(self, "Ошибка", f"В имени задачи используются недопустимые символы. Повторите ввод")
            self.edit_name.setFocus()
            return
        if self.edit_source.text() == "":
            QMessageBox.critical(self, "Ошибка", f"Не указана папка для архивации. Повторите ввод")
            self.edit_source.setFocus()
            return
        if self.edit_destination.text() == "":
            QMessageBox.critical(self, "Ошибка", f"Не указана папка для сохранения архива. Повторите ввод")
            self.edit_destination.setFocus()
            return
        
        if  self.edit_source.text().strip() == self.edit_destination.text().strip():
            QMessageBox.critical(self, "Ошибка", f"Папка для сохранения архива должна отличатся от папки для архивации. Повторите ввод")
            self.edit_destination.setFocus()
            return         
        
        
        # определяем маски
        if not self.mask_check("include", silent=True):
            return
        if not self.mask_check("exclude", silent=True):
            return    

        # проверяем уникальность имени
        for ind, el_task in enumerate(self.config.get("tasks")):
            if el_task.get("name","*") == self.edit_name.text().strip() and ind != self.curr_task_id:
                QMessageBox.critical(self, "Ошибка", f"Не уникальное имя задачи. Повторите ввод")
                self.edit_name.setFocus()
                return

        
        # формируем список дней недели
        day_of_week = []
        for key, button in self.ui_elements.items():
            if key.startswith("btn_day_") :
                for name_day, number_day in day_mapping.items():
                    if key[-1:] == str(number_day) and button.isChecked():
                        day_of_week.append(name_day)                 

        # формируем список дней месяца
        day_of_month =[]
        for key, button in self.ui_elements.items():
            if key.startswith("btn_m_"):
                if button.isChecked():
                    day_of_month.append(int(key[-2:]))
        
        # формируем словарь задачи
        task = {
            "name": self.edit_name.text(),
            "active" : self.btn_active.isChecked(),
            "schedule": "monthly" if self.edit_period.currentIndex()==2 else "weekly" if self.edit_period.currentIndex()==1 else "daily",
            "days_of_week": day_of_week,
            "days_of_month" : day_of_month,
            "time": self.edit_time.text(),
            "source": self.edit_source.text(),
            "destination": self.edit_destination.text(),
            "include_mask": self.curr_include_mask,
            "exclude_mask": self.curr_exclude_mask,
            "direct_to_archive": self.btn_direct_to_archive.isChecked(),
            "compression": "zip_deflated" if self.edit_compression.currentIndex() == 1 else "zip_stored",
            "keep_last": self.edit_keep_last.value(),
            "name1c": self.edit_name1c.text(),
            "dbname": self.edit_dbname.text(),
            "loginwin": self.chk_loginwin.isChecked(),
            "login1c": self.encoder.encode(self.edit_login1c.text())
        }
                
        # """записываем конфигурацию в файла config.yaml."""
        try:
            if self.mode_edit == "ADD":
                # Добавляем новый task в список tasks
                self.config["tasks"].append(task)
            elif self.mode_edit == "EDIT":
                # Обновляем элемент в списке tasks
                self.config["tasks"][self.curr_task_id].update(task)

            # Сохраняем обновленный файл
            with open('config.yaml', "w", encoding="utf-8") as file:
                self.yaml.dump(self.config, file)

        except Exception as e:
            print("Ошибка сохранения конфигурации")
        
        self.data = self.load_config()
        self.refresh_grid()
        # показываем панель грида
        self.frm_edit.setVisible(False)
        self.frm_grid.setVisible(True)  
              
    # записываем общие настройки по вызову из формы настроек
    def save_setting(self, temp_directory, log_retention_days):
        # """записываем конфигурацию в файла config.yaml."""
        try:
            self.config["temp_directory"] = temp_directory
            self.config["log_retention_days"] = log_retention_days

            # Сохраняем обновленный файл
            with open('config.yaml', "w", encoding="utf-8") as file:
                self.yaml.dump(self.config, file)

        except Exception as e:
            print("Ошибка сохранения конфигурации")
        


    ##############################################################################
    # Настройка интерфейса
    #############################################################################
    def setting_ui_element(self):
        
        # включение контекстного меню в гриде
        self.table.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)        
        # привязываем контекстное меню к гриду
        self.table.customContextMenuRequested.connect(self.contextMenuEvent)
        
        
        # показываем панель грида
        self.frm_edit.setVisible(False)
        self.frm_grid.setVisible(True)

        # привязка кнопки отмена и сохранения
        self.btn_cancel.clicked.connect(self.not_save)
        self.btn_save.clicked.connect(self.save_task)

        # привязываем смену выбора комбобокса к таб панели
        self.edit_period.currentIndexChanged.connect(lambda: self.tab_period.setCurrentIndex(self.edit_period.currentIndex()))
        self.tab_period.setCurrentIndex(self.edit_period.currentIndex())
        
        # кнопки проверки масок
        self.btn_check_mask_incl.clicked.connect(lambda: self.mask_check("include"))
        self.btn_check_mask_excl.clicked.connect(lambda: self.mask_check("exclude"))
        
        # кнопки вызова выбора директории
        self.btn_source.clicked.connect(lambda: self.select_folder("Выберите папку для архивирования...", self.edit_source.text(), "source"))
        self.btn_destination.clicked.connect(lambda: self.select_folder("Выберите папку сохранения архива...", self.edit_destination.text(), "destination"))
        
        # реакция кнопок с функцией зажатия
        self.ui_elements = {
            "btn_day_0": self.btn_day_0,
            "btn_day_1": self.btn_day_1,
            "btn_day_2": self.btn_day_2,
            "btn_day_3": self.btn_day_3,
            "btn_day_4": self.btn_day_4,
            "btn_day_5": self.btn_day_5,
            "btn_day_6": self.btn_day_6,
            "active": self.btn_active,
            "btn_m_01" : self.btn_m_01,
            "btn_m_02" : self.btn_m_02,
            "btn_m_03" : self.btn_m_03,
            "btn_m_04" : self.btn_m_04,
            "btn_m_05" : self.btn_m_05,
            "btn_m_06" : self.btn_m_06,
            "btn_m_07" : self.btn_m_07,
            "btn_m_08" : self.btn_m_08,
            "btn_m_09" : self.btn_m_09,
            "btn_m_10" : self.btn_m_10,
            "btn_m_11" : self.btn_m_11,
            "btn_m_12" : self.btn_m_12,
            "btn_m_13" : self.btn_m_13,
            "btn_m_14" : self.btn_m_14,
            "btn_m_15" : self.btn_m_15,
            "btn_m_16" : self.btn_m_16,
            "btn_m_17" : self.btn_m_17,
            "btn_m_18" : self.btn_m_18,
            "btn_m_19" : self.btn_m_19,
            "btn_m_20" : self.btn_m_20,
            "btn_m_21" : self.btn_m_21,
            "btn_m_22" : self.btn_m_22,
            "btn_m_23" : self.btn_m_23,
            "btn_m_24" : self.btn_m_24,
            "btn_m_25" : self.btn_m_25,
            "btn_m_26" : self.btn_m_26,
            "btn_m_27" : self.btn_m_27,
            "btn_m_28" : self.btn_m_28,
            "btn_m_29" : self.btn_m_29,
            "btn_m_30" : self.btn_m_30,
            "btn_m_31" : self.btn_m_31,
            "btn_direct_to_archive" : self.btn_direct_to_archive
        }
        self.button_manager = ButtonManager( self.ui_elements)  

        
        self.btn_active.clicked.connect(lambda: self.button_manager.toggle_button("active", self.btn_active.isChecked()))
        self.btn_day_0.clicked.connect(lambda: self.button_manager.toggle_button("btn_day_0", self.btn_day_0.isChecked()))
        self.btn_day_1.clicked.connect(lambda: self.button_manager.toggle_button("btn_day_1", self.btn_day_1.isChecked()))
        self.btn_day_2.clicked.connect(lambda: self.button_manager.toggle_button("btn_day_2", self.btn_day_2.isChecked()))
        self.btn_day_3.clicked.connect(lambda: self.button_manager.toggle_button("btn_day_3", self.btn_day_3.isChecked()))
        self.btn_day_4.clicked.connect(lambda: self.button_manager.toggle_button("btn_day_4", self.btn_day_4.isChecked()))
        self.btn_day_5.clicked.connect(lambda: self.button_manager.toggle_button("btn_day_5", self.btn_day_5.isChecked()))
        self.btn_day_6.clicked.connect(lambda: self.button_manager.toggle_button("btn_day_6", self.btn_day_6.isChecked()))
        self.btn_m_01.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_01", self.btn_m_01.isChecked()))
        self.btn_m_02.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_02", self.btn_m_02.isChecked()))
        self.btn_m_03.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_03", self.btn_m_03.isChecked()))
        self.btn_m_04.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_04", self.btn_m_04.isChecked()))
        self.btn_m_05.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_05", self.btn_m_05.isChecked()))
        self.btn_m_06.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_06", self.btn_m_06.isChecked()))
        self.btn_m_07.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_07", self.btn_m_07.isChecked()))
        self.btn_m_08.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_08", self.btn_m_08.isChecked()))
        self.btn_m_09.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_09", self.btn_m_09.isChecked()))
        self.btn_m_10.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_10", self.btn_m_10.isChecked()))
        self.btn_m_11.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_11", self.btn_m_11.isChecked()))
        self.btn_m_12.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_12", self.btn_m_12.isChecked()))
        self.btn_m_13.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_13", self.btn_m_13.isChecked()))
        self.btn_m_14.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_14", self.btn_m_14.isChecked()))
        self.btn_m_15.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_15", self.btn_m_15.isChecked()))
        self.btn_m_16.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_16", self.btn_m_16.isChecked()))
        self.btn_m_17.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_17", self.btn_m_17.isChecked()))
        self.btn_m_18.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_18", self.btn_m_18.isChecked()))
        self.btn_m_19.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_19", self.btn_m_19.isChecked()))
        self.btn_m_20.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_20", self.btn_m_20.isChecked()))
        self.btn_m_21.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_21", self.btn_m_21.isChecked()))
        self.btn_m_22.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_22", self.btn_m_22.isChecked()))
        self.btn_m_23.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_23", self.btn_m_23.isChecked()))
        self.btn_m_24.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_24", self.btn_m_24.isChecked()))
        self.btn_m_25.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_25", self.btn_m_25.isChecked()))
        self.btn_m_26.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_26", self.btn_m_26.isChecked()))
        self.btn_m_27.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_27", self.btn_m_27.isChecked()))
        self.btn_m_28.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_28", self.btn_m_28.isChecked()))
        self.btn_m_29.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_29", self.btn_m_29.isChecked()))
        self.btn_m_30.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_30", self.btn_m_30.isChecked()))
        self.btn_m_31.clicked.connect(lambda: self.button_manager.toggle_button("btn_m_31", self.btn_m_31.isChecked()))
        self.btn_direct_to_archive.clicked.connect(lambda: self.button_manager.toggle_button("btn_direct_to_archive", self.btn_direct_to_archive.isChecked()))
 
        # реакция на изменение чекбокса 
        self.chk_loginwin.toggled.connect(self.set_login1c)
 
 
    # устанавливаем доступность корректировки поля пароля 1с
    def set_login1c(self, checked):
        if checked:
            self.lbl_login1c.setEnabled(False)    
            self.edit_login1c.setEnabled(False)
        else:
            self.edit_login1c.setEnabled(True)
            self.lbl_login1c.setEnabled(True)
        
    
    # устанавливаем значение всем кнопками дней недели    
    def set_days_of_week(self, checked=False):
        for key, button in self.ui_elements.items():
            if key.startswith("btn_day_") and button.isChecked() != checked:
                button.click()

    # устанавливаем значение всем кнопками дней месяца
    def set_days_of_month(self, checked=False):
        for key, button in self.ui_elements.items():
            if key.startswith("btn_m_") and button.isChecked() != checked:
                button.click()                
                
    # выставляем по настройкам значение всем кнопками дней недели    
    def read_days_of_week(self, days_of_week):
        for key, button in self.ui_elements.items():
            for name_day in days_of_week:
                if key == f"btn_day_{day_mapping.get(name_day, "")}" :
                    button.click()                 
                    
    # выставляем по настройкам значение всем кнопками дней месяца    
    def read_days_of_month(self, days_of_month):
        for key, button in self.ui_elements.items():
            for day in days_of_month:
                if key == f"btn_m_{str(day).zfill(2)}" :
                    button.click()                                     