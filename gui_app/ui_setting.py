# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_setting.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QSpinBox, QWidget)

class Ui_frmSetting(object):
    def setupUi(self, frmSetting):
        if not frmSetting.objectName():
            frmSetting.setObjectName(u"frmSetting")
        frmSetting.setWindowModality(Qt.WindowModality.ApplicationModal)
        frmSetting.resize(607, 322)
        frmSetting.setMinimumSize(QSize(607, 322))
        frmSetting.setMaximumSize(QSize(607, 322))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        frmSetting.setFont(font)
        self.centralwidget = QWidget(frmSetting)
        self.centralwidget.setObjectName(u"centralwidget")
        self.lbl_log_retention_days = QLabel(self.centralwidget)
        self.lbl_log_retention_days.setObjectName(u"lbl_log_retention_days")
        self.lbl_log_retention_days.setGeometry(QRect(40, 20, 261, 16))
        self.edit_temp_directory = QLineEdit(self.centralwidget)
        self.edit_temp_directory.setObjectName(u"edit_temp_directory")
        self.edit_temp_directory.setGeometry(QRect(160, 60, 381, 22))
        self.edit_temp_directory.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.edit_temp_directory.setReadOnly(True)
        self.lbl_temp_directory = QLabel(self.centralwidget)
        self.lbl_temp_directory.setObjectName(u"lbl_temp_directory")
        self.lbl_temp_directory.setGeometry(QRect(40, 60, 111, 16))
        self.lbl_temp_directory.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.edit_log_retention_days = QSpinBox(self.centralwidget)
        self.edit_log_retention_days.setObjectName(u"edit_log_retention_days")
        self.edit_log_retention_days.setGeometry(QRect(250, 20, 51, 22))
        self.edit_log_retention_days.setMinimum(1)
        self.edit_log_retention_days.setMaximum(30)
        self.edit_log_retention_days.setValue(1)
        self.btn_save = QPushButton(self.centralwidget)
        self.btn_save.setObjectName(u"btn_save")
        self.btn_save.setGeometry(QRect(340, 280, 93, 28))
        self.btn_cancel = QPushButton(self.centralwidget)
        self.btn_cancel.setObjectName(u"btn_cancel")
        self.btn_cancel.setGeometry(QRect(450, 280, 93, 28))
        self.btn_temp_directory = QPushButton(self.centralwidget)
        self.btn_temp_directory.setObjectName(u"btn_temp_directory")
        self.btn_temp_directory.setGeometry(QRect(540, 60, 31, 23))
        self.edit_login = QLineEdit(self.centralwidget)
        self.edit_login.setObjectName(u"edit_login")
        self.edit_login.setGeometry(QRect(160, 130, 181, 20))
        self.edit_password = QLineEdit(self.centralwidget)
        self.edit_password.setObjectName(u"edit_password")
        self.edit_password.setGeometry(QRect(160, 160, 181, 20))
        self.edit_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.lbl_login = QLabel(self.centralwidget)
        self.lbl_login.setObjectName(u"lbl_login")
        self.lbl_login.setGeometry(QRect(40, 130, 101, 16))
        self.lbl_login.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.lbl_password = QLabel(self.centralwidget)
        self.lbl_password.setObjectName(u"lbl_password")
        self.lbl_password.setGeometry(QRect(40, 160, 101, 16))
        self.lbl_password.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.btn_set_schedule = QPushButton(self.centralwidget)
        self.btn_set_schedule.setObjectName(u"btn_set_schedule")
        self.btn_set_schedule.setGeometry(QRect(400, 130, 141, 23))
        self.btn_set_schedule.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        frmSetting.setCentralWidget(self.centralwidget)
        QWidget.setTabOrder(self.edit_log_retention_days, self.btn_temp_directory)
        QWidget.setTabOrder(self.btn_temp_directory, self.edit_login)
        QWidget.setTabOrder(self.edit_login, self.edit_password)
        QWidget.setTabOrder(self.edit_password, self.btn_save)
        QWidget.setTabOrder(self.btn_save, self.btn_cancel)

        self.retranslateUi(frmSetting)

        QMetaObject.connectSlotsByName(frmSetting)
    # setupUi

    def retranslateUi(self, frmSetting):
        frmSetting.setWindowTitle(QCoreApplication.translate("frmSetting", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.lbl_log_retention_days.setText(QCoreApplication.translate("frmSetting", u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0434\u043d\u0435\u0439 \u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f \u043b\u043e\u0433\u043e\u0432", None))
        self.lbl_temp_directory.setText(QCoreApplication.translate("frmSetting", u"\u0412\u0440\u0435\u043c\u0435\u043d\u043d\u0430\u044f \u043f\u0430\u043f\u043a\u0430", None))
        self.btn_save.setText(QCoreApplication.translate("frmSetting", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
        self.btn_cancel.setText(QCoreApplication.translate("frmSetting", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.btn_temp_directory.setText(QCoreApplication.translate("frmSetting", u"...", None))
        self.lbl_login.setText(QCoreApplication.translate("frmSetting", u"\u041b\u043e\u0433\u0438\u043d", None))
        self.lbl_password.setText(QCoreApplication.translate("frmSetting", u"\u041f\u0430\u0440\u043e\u043b\u044c", None))
        self.btn_set_schedule.setText(QCoreApplication.translate("frmSetting", u"\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c \u0441\u043b\u0443\u0436\u0431\u0443", None))
    # retranslateUi

