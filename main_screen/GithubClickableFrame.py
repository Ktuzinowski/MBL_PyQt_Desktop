from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QCursor, QDesktopServices


class GithubClickableFrame(QFrame):
    def __init__(self, parent=None):
        super(GithubClickableFrame, self).__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        QDesktopServices.openUrl(QUrl("https://github.com/Ktuzinowski/MBL_PyQt_Desktop"))
