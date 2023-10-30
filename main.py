import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Window(QWidget):
   def __init__(self):
      super(Window, self).__init__()
      self.initUI()

   def initUI(self):
      hbox = QHBoxLayout(self)

      leftFrame = QFrame()
      leftFrame.setFrameShape(QFrame.StyledPanel)

      middleFrame = QFrame()
      middleFrame.setFrameShape(QFrame.StyledPanel)

      rightFrame = QFrame()
      rightFrame.setFrameShape(QFrame.StyledPanel)

      splitter = QSplitter(Qt.Horizontal)
      splitter.addWidget(leftFrame)
      splitter.addWidget(middleFrame)
      splitter.addWidget(rightFrame)
      splitter.setSizes([300,800,300])

      hbox.addWidget(splitter)

      self.setLayout(hbox)
      QApplication.setStyle(QStyleFactory.create('Cleanlooks'))

      self.setGeometry(0,0, 800, 800)
      self.setWindowTitle("MBL Visualizer")
      self.show()
      
def main():
   app = QApplication(sys.argv)
   ex = Window()
   sys.exit(app.exec_())
   
if __name__ == '__main__':
   main()