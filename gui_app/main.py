from PyQt6 import QtWidgets
from PyQt6.QtGui import QFont
from gui_app.MainWindow import MainWindow
import sys

def main():

    app = QtWidgets.QApplication([])
    # стиль приложения
    app.setStyle('Fusion')
    app.setFont(QFont('Arial', 9))
    
    application = MainWindow()
    
    application.show()
    
    sys.exit(app.exec())