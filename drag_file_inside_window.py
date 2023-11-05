from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidgetItem
import sys

from list_box_widget import ListboxWidget


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MBL Visualizer")
        self.setWindowIcon(QIcon("wolf.png"))

        self.setGeometry(150, 150, 1200, 600)

        self.list_view = ListboxWidget(self)

        self.select_file_button = QPushButton('Get Value', self)
        self.select_file_button.setGeometry(800,300,200,50)






app = QApplication([])
window = Window()

window.show()
sys.exit(app.exec())
