import os
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QRect, QPropertyAnimation

# IMPORT GUI FILE
from ui_interface import *

# IMPORT PYSIDE
from PySide2.QtGui import QPainter
from PySide2.QtCharts import QtCharts

# Import Functool
from functools import partial

from Custom_Widgets.Widgets import *

import csv

from ui_interface import *

shadow_elements = {
    "frame_3",
    "frame_5",
    "header_frame",
    "frame_8"
}

# MAIN WINDOW CLASS
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set Window Minimum Size
        self.setMinimumSize(850, 600)
        self.button_navigation()
        self.setup_expand_and_open_for_menu()

        loadJsonStyle(self, self.ui)

        for x in shadow_elements:
            # Shadow effect style
            effect = QtWidgets.QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(18)
            effect.setYOffset(0)
            effect.setXOffset(0)
            effect.setColor(QColor(0, 0, 0, 255))
            getattr(self.ui, x).setGraphicsEffect(effect)

        # Manually Setup Navigation to Other Windows


        # SHOW WINDOW
        self.show()

    def setup_expand_and_open_for_menu(self):
        self.ui.open_close_side_bar_btn.clicked.connect(lambda: self.toggle_menu_left_widget())
    def toggle_menu_left_widget(self):
        print("CLICKING TOGGLE")
        if self.ui.left_menu_frame.isHidden():
            self.ui.left_menu_frame.show()
            self.setMinimumSize(850, self.minimumHeight() + 1)
        else:
            self.ui.left_menu_frame.hide()

    def button_navigation(self):
        self.ui.percentage_bar_btn.clicked.connect(lambda: self.display(0))
        self.ui.temperature_bar_btn.clicked.connect(lambda: self.display(1))
        self.ui.nested_donut_btn.clicked.connect(lambda: self.display(2))
        self.ui.line_chart_btn.clicked.connect(lambda: self.display(3))
        self.ui.bar_charts_btn.clicked.connect(lambda: self.display(4))
    def display(self, i):
        self.ui.stackedWidget.setCurrentIndex(i)


# EXECUTE APP
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
