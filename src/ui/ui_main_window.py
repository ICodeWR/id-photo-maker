# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QSplitter, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1100, 720)
        MainWindow.setStyleSheet(u"\n"
"    /* \u2500\u2500 \u7d27\u51d1\u5de5\u5177\u680f\u6837\u5f0f \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */\n"
"    QMainWindow, QWidget { font-size: 13px; }\n"
"    QPushButton {\n"
"        padding: 4px 12px;\n"
"        border: 1px solid #ccc;\n"
"        border-radius: 4px;\n"
"        background: #f8f8f8;\n"
"        min-height: 20px;\n"
"        max-height: 28px;\n"
"    }\n"
"    QPushButton:hover {\n"
"        background: #e8e8e8;\n"
"        border-color: #aaa;\n"
"    }\n"
"    QPushButton:pressed {\n"
"        background: #d8d8d8;\n"
"    }\n"
"    QComboBox {\n"
"        padding: 2px 6px;\n"
"        min-height: 20px;\n"
"        max-height: 26px;\n"
"        border: 1px solid #bbb;\n"
"        border-radius: 4px;\n"
"        background: white;\n"
"    }\n"
"    QLabel { padding: 0 4px; }\n"
"    QStatusBar { font-size: 12px; }\n"
"   ")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralLayout = QVBoxLayout(self.centralwidget)
        self.centralLayout.setObjectName(u"centralLayout")
        self.toolbar = QWidget(self.centralwidget)
        self.toolbar.setObjectName(u"toolbar")
        self.toolbar.setMaximumSize(QSize(16777215, 36))
        self.toolbarLayout = QHBoxLayout(self.toolbar)
        self.toolbarLayout.setSpacing(0)
        self.toolbarLayout.setObjectName(u"toolbarLayout")
        self.btn_upload = QPushButton(self.toolbar)
        self.btn_upload.setObjectName(u"btn_upload")

        self.toolbarLayout.addWidget(self.btn_upload)

        self.btn_camera = QPushButton(self.toolbar)
        self.btn_camera.setObjectName(u"btn_camera")

        self.toolbarLayout.addWidget(self.btn_camera)

        self.btn_capture = QPushButton(self.toolbar)
        self.btn_capture.setObjectName(u"btn_capture")

        self.toolbarLayout.addWidget(self.btn_capture)

        self.toolbarSpacerLeft = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarLayout.addItem(self.toolbarSpacerLeft)

        self.lbl_bg_color = QLabel(self.toolbar)
        self.lbl_bg_color.setObjectName(u"lbl_bg_color")

        self.toolbarLayout.addWidget(self.lbl_bg_color)

        self.combo_bg = QComboBox(self.toolbar)
        self.combo_bg.addItem("")
        self.combo_bg.addItem("")
        self.combo_bg.addItem("")
        self.combo_bg.addItem("")
        self.combo_bg.addItem("")
        self.combo_bg.setObjectName(u"combo_bg")
        self.combo_bg.setMinimumSize(QSize(80, 0))

        self.toolbarLayout.addWidget(self.combo_bg)

        self.lbl_size = QLabel(self.toolbar)
        self.lbl_size.setObjectName(u"lbl_size")

        self.toolbarLayout.addWidget(self.lbl_size)

        self.combo_size = QComboBox(self.toolbar)
        self.combo_size.addItem("")
        self.combo_size.addItem("")
        self.combo_size.addItem("")
        self.combo_size.addItem("")
        self.combo_size.addItem("")
        self.combo_size.addItem("")
        self.combo_size.addItem("")
        self.combo_size.addItem("")
        self.combo_size.addItem("")
        self.combo_size.addItem("")
        self.combo_size.addItem("")
        self.combo_size.setObjectName(u"combo_size")
        self.combo_size.setMinimumSize(QSize(80, 0))

        self.toolbarLayout.addWidget(self.combo_size)

        self.toolbarSpacerRight = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarLayout.addItem(self.toolbarSpacerRight)

        self.btn_save = QPushButton(self.toolbar)
        self.btn_save.setObjectName(u"btn_save")

        self.toolbarLayout.addWidget(self.btn_save)


        self.centralLayout.addWidget(self.toolbar)

        self.workSplitter = QSplitter(self.centralwidget)
        self.workSplitter.setObjectName(u"workSplitter")
        self.workSplitter.setOrientation(Qt.Horizontal)
        self.leftScrollArea = QScrollArea(self.workSplitter)
        self.leftScrollArea.setObjectName(u"leftScrollArea")
        self.leftScrollArea.setWidgetResizable(True)
        self.leftScrollArea.setMinimumSize(QSize(400, 0))
        self.leftScrollContents = QWidget()
        self.leftScrollContents.setObjectName(u"leftScrollContents")
        self.leftScrollContents.setGeometry(QRect(0, 0, 400, 600))
        self.leftScrollLayout = QVBoxLayout(self.leftScrollContents)
        self.leftScrollLayout.setObjectName(u"leftScrollLayout")
        self.label_original = QLabel(self.leftScrollContents)
        self.label_original.setObjectName(u"label_original")
        self.label_original.setAlignment(Qt.AlignCenter)
        self.label_original.setStyleSheet(u"background-color: #e8e8e8; color: #999;")

        self.leftScrollLayout.addWidget(self.label_original)

        self.leftScrollArea.setWidget(self.leftScrollContents)
        self.workSplitter.addWidget(self.leftScrollArea)
        self.rightScrollArea = QScrollArea(self.workSplitter)
        self.rightScrollArea.setObjectName(u"rightScrollArea")
        self.rightScrollArea.setWidgetResizable(True)
        self.rightScrollArea.setMinimumSize(QSize(320, 0))
        self.rightScrollContents = QWidget()
        self.rightScrollContents.setObjectName(u"rightScrollContents")
        self.rightScrollContents.setGeometry(QRect(0, 0, 320, 600))
        self.rightScrollLayout = QVBoxLayout(self.rightScrollContents)
        self.rightScrollLayout.setObjectName(u"rightScrollLayout")
        self.label_preview = QLabel(self.rightScrollContents)
        self.label_preview.setObjectName(u"label_preview")
        self.label_preview.setAlignment(Qt.AlignCenter)
        self.label_preview.setStyleSheet(u"background-color: #eeeeee; color: #bbb;")

        self.rightScrollLayout.addWidget(self.label_preview)

        self.rightScrollArea.setWidget(self.rightScrollContents)
        self.workSplitter.addWidget(self.rightScrollArea)

        self.centralLayout.addWidget(self.workSplitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u667a\u80fd\u8bc1\u4ef6\u7167\u5236\u4f5c\u5de5\u5177", None))
        self.btn_upload.setText(QCoreApplication.translate("MainWindow", u"\U0001f4c1 \U00004e0a\U00004f20\U000056fe\U00007247", None))
        self.btn_camera.setText(QCoreApplication.translate("MainWindow", u"\U0001f4f7 \U00006253\U00005f00\U00006444\U000050cf\U00005934", None))
        self.btn_capture.setText(QCoreApplication.translate("MainWindow", u"\U0001f4f8 \U000062cd\U00007167", None))
        self.lbl_bg_color.setText(QCoreApplication.translate("MainWindow", u"\u80cc\u666f\u8272\uff1a", None))
        self.combo_bg.setItemText(0, QCoreApplication.translate("MainWindow", u"\u7ea2\u8272", None))
        self.combo_bg.setItemText(1, QCoreApplication.translate("MainWindow", u"\u84dd\u8272", None))
        self.combo_bg.setItemText(2, QCoreApplication.translate("MainWindow", u"\u767d\u8272", None))
        self.combo_bg.setItemText(3, QCoreApplication.translate("MainWindow", u"\u7070\u8272", None))
        self.combo_bg.setItemText(4, QCoreApplication.translate("MainWindow", u"\u7eff\u8272", None))

        self.combo_bg.setCurrentText(QCoreApplication.translate("MainWindow", u"\u7ea2\u8272", None))
        self.lbl_size.setText(QCoreApplication.translate("MainWindow", u"\u5c3a\u5bf8\uff1a", None))
        self.combo_size.setItemText(0, QCoreApplication.translate("MainWindow", u"\u4e00\u5bf8", None))
        self.combo_size.setItemText(1, QCoreApplication.translate("MainWindow", u"\u4e8c\u5bf8", None))
        self.combo_size.setItemText(2, QCoreApplication.translate("MainWindow", u"\u5c0f\u4e00\u5bf8", None))
        self.combo_size.setItemText(3, QCoreApplication.translate("MainWindow", u"\u5927\u4e00\u5bf8", None))
        self.combo_size.setItemText(4, QCoreApplication.translate("MainWindow", u"\u5c0f\u4e8c\u5bf8", None))
        self.combo_size.setItemText(5, QCoreApplication.translate("MainWindow", u"\u5927\u4e8c\u5bf8", None))
        self.combo_size.setItemText(6, QCoreApplication.translate("MainWindow", u"\u4e09\u5bf8", None))
        self.combo_size.setItemText(7, QCoreApplication.translate("MainWindow", u"\u4e94\u5bf8", None))
        self.combo_size.setItemText(8, QCoreApplication.translate("MainWindow", u"\u62a4\u7167", None))
        self.combo_size.setItemText(9, QCoreApplication.translate("MainWindow", u"\u7b7e\u8bc1", None))
        self.combo_size.setItemText(10, QCoreApplication.translate("MainWindow", u"\u9a7e\u9a76\u8bc1", None))

        self.combo_size.setCurrentText(QCoreApplication.translate("MainWindow", u"\u4e00\u5bf8", None))
        self.btn_save.setText(QCoreApplication.translate("MainWindow", u"\U0001f4be \U00004fdd\U00005b58\U000056fe\U00007247", None))
        self.label_original.setText(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u300c\u4e0a\u4f20\u56fe\u7247\u300d\u5f00\u59cb", None))
        self.label_preview.setText(QCoreApplication.translate("MainWindow", u"\u9884\u89c8\u533a", None))
#if QT_CONFIG(statustip)
        self.statusbar.setStatusTip("")
#endif // QT_CONFIG(statustip)
    # retranslateUi

