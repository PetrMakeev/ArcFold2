from datetime import datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import QModelIndex

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