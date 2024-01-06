from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QGraphicsView, QPushButton, QDoubleSpinBox, QComboBox, QProgressBar
import numpy as np
import os
import pyqtgraph as pg
from cellpose import models
from cellpose.io import imread, imsave, outlines_to_text, add_model, remove_model, save_rois

from myWidgets import PhotoViewer


def avg3d(C):
    """
    smooth value of c across nearby points
    (c is center of grid directly below point
    b -- a -- b
    a -- c -- a
    b -- a -- b
    """

    Ly, Lx = C.shape
    # pad T by 2
    T = np.zeros((Ly + 2, Lx + 2), np.float32)
    M = np.zeros((Ly, Lx), np.float32)
    T[1:-1, 1:-1] = C.copy()
    y, x = np.meshgrid(np.arange(0, Ly, 1, int), np.arange(0, Lx, 1, int), indexing='ij')
    y += 1
    x += 1
    a = 1. / 2  # /(z**2 + 1) ** 0.5
    b = 1. / (1 + 2 ** 0.5)  # (z**2 + 2) ** 0.5
    c = 1.
    M = (b * T[y - 1, x - 1] + a * T[y - 1, x] + b * T[y - 1, x + 1] +
         a * T[y, x - 1] + c * T[y, x] + a * T[y, x + 1] +
         b * T[y + 1, x - 1] + a * T[y + 1, x] + b * T[y + 1, x + 1])
    M /= 4 * a + 4 * b + c
    return M


def interpZ(mask, zdraw):
    """ find nearby planes and average their values using grid of points
        zfill is in ascending order
    """
    ifill = np.ones(mask.shape[0], "bool")
    zall = np.arange(0, mask.shape[0], 1, int)
    ifill[zdraw] = False
    zfill = zall[ifill]
    zlower = zdraw[np.searchsorted(zdraw, zfill, side='left') - 1]
    zupper = zdraw[np.searchsorted(zdraw, zfill, side='right')]
    for k, z in enumerate(zfill):
        Z = zupper[k] - zlower[k]
        zl = (z - zlower[k]) / Z
        plower = avg3d(mask[zlower[k]]) * (1 - zl)
        pupper = avg3d(mask[zupper[k]]) * zl
        mask[z] = (plower + pupper) > 0.33
        # Ml, norml = avg3d(mask[zlower[k]], zl)
        # Mu, normu = avg3d(mask[zupper[k]], 1-zl)
        # mask[z] = (Ml + Mu) / (norml + normu)  > 0.5
    return mask, zfill


def make_bwr():
    # make a bwr colormap
    b = np.append(255 * np.ones(128), np.linspace(0, 255, 128)[::-1])[:, np.newaxis]
    r = np.append(np.linspace(0, 255, 128), 255 * np.ones(128))[:, np.newaxis]
    g = np.append(np.linspace(0, 255, 128), np.linspace(0, 255, 128)[::-1])[:, np.newaxis]
    color = np.concatenate((r, g, b), axis=-1).astype(np.uint8)
    bwr = pg.ColorMap(pos=np.linspace(0.0, 255, 256), color=color)
    return bwr


def make_spectral():
    # make spectral colormap
    r = np.array(
        [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108,
         112, 116, 120, 124, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 120,
         112, 104, 96, 88, 80, 72, 64, 56, 48, 40, 32, 24, 16, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63, 67,
         71, 75, 79, 83, 87, 91, 95, 99, 103, 107, 111, 115, 119, 123, 127, 131, 135, 139, 143, 147, 151, 155, 159, 163,
         167, 171, 175, 179, 183, 187, 191, 195, 199, 203, 207, 211, 215, 219, 223, 227, 231, 235, 239, 243, 247, 251,
         255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
         255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
         255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
         255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
         255, 255, 255, 255, 255, 255, 255, 255])
    g = np.array(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 9, 9, 8, 8, 7, 7, 6, 6, 5, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0, 0, 0, 7, 15, 23,
         31, 39, 47, 55, 63, 71, 79, 87, 95, 103, 111, 119, 127, 135, 143, 151, 159, 167, 175, 183, 191, 199, 207, 215,
         223, 231, 239, 247, 255, 247, 239, 231, 223, 215, 207, 199, 191, 183, 175, 167, 159, 151, 143, 135, 128, 129,
         131, 132, 134, 135, 137, 139, 140, 142, 143, 145, 147, 148, 150, 151, 153, 154, 156, 158, 159, 161, 162, 164,
         166, 167, 169, 170, 172, 174, 175, 177, 178, 180, 181, 183, 185, 186, 188, 189, 191, 193, 194, 196, 197, 199,
         201, 202, 204, 205, 207, 208, 210, 212, 213, 215, 216, 218, 220, 221, 223, 224, 226, 228, 229, 231, 232, 234,
         235, 237, 239, 240, 242, 243, 245, 247, 248, 250, 251, 253, 255, 251, 247, 243, 239, 235, 231, 227, 223, 219,
         215, 211, 207, 203, 199, 195, 191, 187, 183, 179, 175, 171, 167, 163, 159, 155, 151, 147, 143, 139, 135, 131,
         127, 123, 119, 115, 111, 107, 103, 99, 95, 91, 87, 83, 79, 75, 71, 67, 63, 59, 55, 51, 47, 43, 39, 35, 31, 27,
         23, 19, 15, 11, 7, 3, 0, 8, 16, 24, 32, 41, 49, 57, 65, 74, 82, 90, 98, 106, 115, 123, 131, 139, 148, 156, 164,
         172, 180, 189, 197, 205, 213, 222, 230, 238, 246, 254])
    b = np.array(
        [0, 7, 15, 23, 31, 39, 47, 55, 63, 71, 79, 87, 95, 103, 111, 119, 127, 135, 143, 151, 159, 167, 175, 183, 191,
         199, 207, 215, 223, 231, 239, 247, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
         255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 251, 247, 243, 239,
         235, 231, 227, 223, 219, 215, 211, 207, 203, 199, 195, 191, 187, 183, 179, 175, 171, 167, 163, 159, 155, 151,
         147, 143, 139, 135, 131, 128, 126, 124, 122, 120, 118, 116, 114, 112, 110, 108, 106, 104, 102, 100, 98, 96, 94,
         92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60, 58, 56, 54, 52, 50, 48, 46, 44, 42, 40, 38,
         36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 16, 24, 32, 41, 49, 57, 65, 74, 82, 90, 98, 106, 115, 123, 131,
         139, 148, 156, 164, 172, 180, 189, 197, 205, 213, 222, 230, 238, 246, 254])
    color = np.vstack((r, g, b)).T.astype(np.uint8)
    spectral = pg.ColorMap(pos=np.linspace(0.0, 255, 256), color=color)
    return spectral


def make_cmap(cm=0):
    # make a single channel colormap
    r = np.arange(0, 256)
    color = np.zeros((256, 3))
    color[:, cm] = r
    color = color.astype(np.uint8)
    cmap = pg.ColorMap(pos=np.linspace(0.0, 255, 256), color=color)
    return cmap


class SegmentationFrameContainer(QFrame):

    def __init__(self, parent=None):
        super(SegmentationFrameContainer, self).__init__(parent)
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


class SegmentationParameterListFrameContainer(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        # Timer to load in components before hooking up the corresponding buttons
        self.model = None
        self.current_model_path = None
        self.diameter = None
        self.calibrationValue = None
        self.current_model = None
        self.calibrateButton = None
        self.firstChannel = None
        self.secondChannel = None
        self.progress_bar = None
        self.modelToRun = None
        self.NZ, self.Ly, self.Lx = 1, 512, 512
        self.stack = np.zeros((1, self.Ly, self.Lx, 3))
        QTimer.singleShot(50, self.setup_ui_elements)

    def setup_ui_elements(self):
        self.setup_calibration_functionality()
        self.setup_channel_combo_boxes()
        self.setup_progress_bar()

    def setup_model_combo_box(self):
        self.modelToRun = self.findChild(QComboBox, "modelToRun")
        if self.modelToRun:
            print("was able to get the correct model to run comboBox")
        else:
            print("was not able to get the correct combobox to select")

    def setup_progress_bar(self):
        self.progress_bar = self.findChild(QProgressBar, "progressBar")
        if self.progress_bar:
            print("was able to retrieve the progress bar")
        else:
            print("failed to retrieve the progress bar")

    def setup_channel_combo_boxes(self):
        self.firstChannel = self.findChild(QComboBox, "firstChannel")
        if self.firstChannel:
            print("Correctly setup the first channel")
        else:
            print("failed to get the first channel")

        self.secondChannel = self.findChild(QComboBox, "secondChannel")
        if self.secondChannel:
            print("Correctly setup the first channel")
        else:
            print("failed to get the first channel")

    def setup_calibration_functionality(self):
        self.calibrateButton = self.findChild(QPushButton, "calibrateButton")
        if self.calibrateButton:
            self.calibrateButton.clicked.connect(self.calibrate_for_cell_diameter)
        else:
            print("could not find calibrate button")
        self.calibrationValue = self.findChild(QDoubleSpinBox, "calibrationValue")
        if self.calibrationValue:
            print("Calibration default value", self.calibrationValue.value())
        else:
            print("could not find calibration value double spin box")

    def list_all_children(self):
        # Retrieve all children of the frame (including promoted components)
        all_children = self.findChildren(object)

        # Print out information about each child
        for child in all_children:
            print(f"Object Name: {child.objectName()}, Class Name: {child.__class__.__name__}")

    def calibrate_for_cell_diameter(self):
        self.initialize_model(model_name='cyto')
        print(self.current_model)
        diameter, _ = self.model.sz.eval(self.stack[self.currentZ].copy(), channels=self.get_channels(), progress=self.progress)
        diameter = np.maximum(5.0, diameter)
        print('estimated diameter of cells using %s model = %0.1f pixels' % (self.current_model, diameter))
        self.calibrationValue.setValue(diameter)
        self.diameter = diameter
        self.progress.setValue(100)

    def get_channels(self):
        channels = [self.firstChannel.currentIndex(), self.secondChannel.currentIndex()]
        if self.current_model == 'nuclei':
            channels[1] = 0
        return channels

    def initialize_model(self, model_name=None):
        if model_name is None or not isinstance(model_name, str):
            self.get_model_path()
            self.model = models.CellposeModel(gpu=False, pretrained_model=self.current_model_path)
            print('ONE: This should be initializing the model currently')
        else:
            self.current_model = model_name
            if 'cyto' in self.current_model or 'nuclei' in self.current_model:
                self.current_model_path = models.model_path(self.current_model, 0)
                print('TWO: This should be initializing the model currently')
            else:
                self.current_model_path = os.fspath(models.MODEL_DIR.joinpath(self.current_model))
                print('THREE: This should be initializing the model currently')
            if self.current_model == 'cyto':
                self.model = models.CellposeModel(gpu=False, model_type=self.current_model)
                print('FOUR: This should be initializing the model currently')
            else:
                self.model = models.CellposeModel(gpu=False, model_type=self.current_model)
                print('FIVE: This should be initializing the model currently')

    def get_model_path(self):
        self.current_model = self.modelToRun.currentText()
        self.current_model_path = os.fspath(models.MODEL_DIR.joinpath(self.current_model))
