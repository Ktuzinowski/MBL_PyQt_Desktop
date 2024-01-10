from PyQt5.QtWidgets import QFrame, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRectF
from PyQt5.QtGui import QPixmap, QColor, QBrush, QImage, QTransform
import os
import cv2
import pandas as pd

from protein_screen import GlobalObject
import tifffile

from protein_screen import file_checker_util as file_check


class PhotoViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)

    def __init__(self, parent=None):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)

    def has_photo(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.has_photo():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                factor *= 0.97
                self.scale(factor, factor)
            self._zoom = 0

    def set_photo(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.has_photo():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime_data_urls = event.mimeData().urls()
        accepted_event = False
        for url_file in mime_data_urls:
            if file_check.check_file_extension(url_file.fileName()):
                event.setDropAction(Qt.CopyAction)
                file_path = event.mimeData().urls()[0].toLocalFile()
                self.set_image(file_path)
                accepted_event = True
                event.accept()
            elif file_check.check_file_for_excel(url_file.fileName()):
                event.setDropAction(Qt.CopyAction)
                file_path = event.mimeData().urls()[0].toLocalFile()
                GlobalObject().data_frame = pd.read_excel(file_path)
                GlobalObject().dispatch_event("NEW_DATA")
                accepted_event = True
                event.accept()
            else:
                directory = url_file.path()
                directory2 = url_file.path().replace(directory[0], "", 1)
                if os.path.isdir(directory2):
                    array_of_new_img_files = []
                    for filename in os.listdir(directory2):
                        f = os.path.join(directory2, filename)
                        if file_check.check_file_for_new_image(f):
                            img_file = cv2.imread(f)
                            array_of_new_img_files.append(img_file)
                    new_image = cv2.hconcat(array_of_new_img_files)
                    # Create New Image File Location
                    new_file_location = os.path.join(directory2, "output_image.tif")
                    cv2.imwrite(new_file_location, new_image)
                    self.set_image(new_file_location)
                else:
                    print("this is failing")

        if not accepted_event:
            event.ignore()

    def set_image(self, file_path):
        if file_check.check_file_for_tif_image(file_path):
            print("trying to add in the tif file")
            tif_data = tifffile.imread(file_path)
            print(tif_data)
            height, width = tif_data.shape
            bytes_per_line = 2 * width
            print(width, height, bytes_per_line)
            img_scaled = cv2.normalize(tif_data, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)
            image = QImage(img_scaled.data, width, height, bytes_per_line, QImage.Format_Grayscale16)
            print("image ", image)
            pixmap = QPixmap.fromImage(image)
            print("pixmap ", pixmap)
            self.set_photo(pixmap)
        else:
            image = QImage(file_path)
            pixmap = QPixmap.fromImage(image.transformed(QTransform().rotate(90)))
            self.set_photo(pixmap)
