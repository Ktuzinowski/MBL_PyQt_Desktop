from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

def window():
	# Based on OS getting application running
	app = QApplication(sys.argv)
	win = QMainWindow()
	win.setGeometry(200, 200, 300, 300)
	win.setWindowTitle("MBL PyQt")

	win.show()
	sys.exit(app.exec_())

window()
