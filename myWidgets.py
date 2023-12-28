import functools

from PyQt5.QtWidgets import QLabel, QSlider, QCheckBox, QComboBox, QSizePolicy, QVBoxLayout, QFrame, QGraphicsView, \
    QGraphicsScene, QHBoxLayout, QGraphicsPixmapItem, QColorDialog
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRectF, QSize, QCoreApplication, QUrl
from PyQt5.QtGui import QPixmap, QColor, QBrush, QImage, QCursor, QDesktopServices
import os
import re
import cv2
import pandas as pd
from globalobject import GlobalObject
import tifffile


def check_file_for_new_image(filename):
    # Regular expression to match file extensions .tif, .tiff, .jpg, or .png
    pattern = r"1\.(tif|tiff|jpg|png)$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        return True
    else:
        return False


def check_file_for_tif_image(filename):
    # Regular expression to match .tif file
    pattern = r"\.(tif|tiff)$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        return True
    else:
        return False


def check_file_for_excel(filename):
    # Regular expression to match file extensions .xlsx
    pattern = r"\.(xlsx)$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        return True
    else:
        return False


def check_file_extension(filename):
    # Regular expression to match file extensions .tif, .tiff, .jpg, or .png
    pattern = r"\.(tif|tiff|jpg|png)$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        return True
    else:
        return False


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
            if check_file_extension(url_file.fileName()):
                event.setDropAction(Qt.CopyAction)
                file_path = event.mimeData().urls()[0].toLocalFile()
                self.set_image(file_path)
                accepted_event = True
                event.accept()
            elif check_file_for_excel(url_file.fileName()):
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
                        if check_file_for_new_image(f):
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
        if check_file_for_tif_image(file_path):
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
            self.set_photo(QPixmap(file_path))


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


class SliderForProteinFrame(QFrame):
    def __init__(self, parent=None, column_names=None, color_for_display=None, current_list_index=0):
        super(SliderForProteinFrame, self).__init__(parent)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
        self.setMaximumSize(QSize(300, 80))
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("frame_32")

        self.verticalLayout_17 = QVBoxLayout(self)
        self.verticalLayout_17.setContentsMargins(8, 8, 8, -1)
        self.verticalLayout_17.setObjectName("verticalLayout_18")

        # Check Box and Combo Box Frame
        self.frame_11 = QFrame(self)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(size_policy)
        self.frame_11.setMaximumSize(QSize(300, 50))
        self.frame_11.setFrameShape(QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Raised)
        self.frame_11.setObjectName("frame_12")

        # Horizontal for Combo Box and Check Box
        self.horizontalLayout_4 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_6")
        # Create Combo Box
        self.comboBox_14 = QComboBox(self.frame_11)
        self.comboBox_14.setStyleSheet("QComboBox { padding: 4px; }")
        self.comboBox_14.setObjectName("comboBox_17")
        for _ in column_names:
            self.comboBox_14.addItem("")
        self.horizontalLayout_4.addWidget(self.comboBox_14)
        # Create Check Box
        self.checkBox_7 = QCheckBox(self.frame_11)
        self.checkBox_7.setObjectName("checkBox_8")

        self.horizontalLayout_4.addWidget(self.checkBox_7)
        self.verticalLayout_17.addWidget(self.frame_11)

        # Create Frame for Slider and Color Block
        self.frame_10 = QFrame(self)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.frame_10.sizePolicy().hasHeightForWidth())
        self.frame_10.setSizePolicy(size_policy)
        self.frame_10.setMaximumSize(QSize(300, 50))
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.frame_10.setObjectName("frame_11")
        self.horizontalLayout_3 = QHBoxLayout(self.frame_10)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_4")
        self.horizontalSlider_7 = QSlider(self.frame_10)
        self.horizontalSlider_7.setOrientation(Qt.Horizontal)
        self.horizontalSlider_7.setObjectName("horizontalSlider_8")
        self.horizontalLayout_3.addWidget(self.horizontalSlider_7)
        self.label_5 = QLabel(self.frame_10)
        size_of_label_5 = 26
        self.label_5.setMinimumSize(QSize(size_of_label_5, size_of_label_5))
        self.label_5.setMaximumSize(QSize(size_of_label_5, size_of_label_5))
        self.label_5.setAutoFillBackground(False)
        self.label_5.setStyleSheet(
            "background-color: " + color_for_display + "; "
            + "border-radius: " + "13px" + "; "
        )
        self.label_5.mousePressEvent = functools.partial(self.color_block_clicked, source_object=self.label_5)
        self.label_5.setText("")
        self.label_5.setObjectName("label_6")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.verticalLayout_17.addWidget(self.frame_10)
        _translate = QCoreApplication.translate

        counter = 0
        for column in column_names:
            if column == "Areax":
                continue
            elif column == "AreaY":
                continue
            elif column == "LocalX":
                continue
            elif column == "LocalY":
                continue
            elif column == "GlobX":
                continue
            elif column == "GlobY":
                continue
            self.comboBox_14.setItemText(counter, _translate("MainWindow", column))
            counter += 1
        self.comboBox_14.setCurrentIndex(current_list_index)

    def color_block_clicked(self, event, source_object=None):
        color = QColorDialog.getColor()
        if color.isValid():
            self.label_5.setStyleSheet(
                "background-color: {}".format(color.name()) + "; " + "border-radius: " + "13px" + ";")


class LabClickableFrame(QFrame):
    def __init__(self, parent=None):
        super(LabClickableFrame, self).__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        QDesktopServices.openUrl(QUrl("https://www.multiplexbiotechnologylab.com/"))


class GithubClickableFrame(QFrame):
    def __init__(self, parent=None):
        super(GithubClickableFrame, self).__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        QDesktopServices.openUrl(QUrl("https://github.com/Ktuzinowski/MBL_PyQt_Desktop"))
