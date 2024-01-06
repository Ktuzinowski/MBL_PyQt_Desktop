from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QCursor, QDesktopServices


class LabClickableFrame(QFrame):
    def __init__(self, parent=None):
        super(LabClickableFrame, self).__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        QDesktopServices.openUrl(QUrl("https://www.multiplexbiotechnologylab.com/"))
