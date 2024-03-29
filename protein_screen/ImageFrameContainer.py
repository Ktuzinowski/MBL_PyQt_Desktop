from PyQt5.QtWidgets import QVBoxLayout, QFrame, QGraphicsView
from protein_screen import PhotoViewer


class ImageFrameContainer(QFrame):
    def __init__(self, parent=None):
        super(ImageFrameContainer, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setContentsMargins(0, 0, 0, 0)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.photoViewer = PhotoViewer(self)
        main_layout.addWidget(self.photoViewer)

        self.setLayout(main_layout)

    def photo_clicked(self, pos):
        if self.viewer.dragMode() == QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))
