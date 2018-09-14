# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWebEngineWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, resolution, url):
        MainWindow.setObjectName("MainWindow")
        # MainWindow.showMaximized()
        MainWindow.resize(*resolution)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.webView = QtWebEngineWidgets.QWebEngineView(self.centralwidget)
        self.webView.setUrl(QtCore.QUrl(url))
        self.webView.setObjectName("webView")
        self.gridLayout.addWidget(self.webView, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        # self.statusbar = QtWidgets.QStatusBar(MainWindow)
        # self.statusbar.setObjectName("statusbar")
        # MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Artex", "Artex"))


if __name__ == "__main__":
    url = sys.argv[1]
    app = QtWidgets.QApplication([])
    # app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling) - doesn't work
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, resolution=(1280, 768), url=url)
    MainWindow.show()
    sys.exit(app.exec_())
