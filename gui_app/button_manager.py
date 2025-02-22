from PyQt6.QtGui import QFont

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
