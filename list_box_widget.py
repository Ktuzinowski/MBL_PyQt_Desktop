from PyQt6.QtWidgets import QFileDialog, QListView
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QUrl


class ListboxWidget(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.possible_files_to_use = None
        self.setAcceptDrops(True)
        self.resize(600, 600)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(ListboxWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(ListboxWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            links = []
            for url in event.mimeData().urls():
                print(url)
                links.append(str(url.toLocalFile()))
            self.possible_files_to_use = links
        else:
            super(ListboxWidget, self).dropEvent(event)
