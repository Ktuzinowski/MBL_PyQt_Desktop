from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFrame, QComboBox, QProgressBar, QRadioButton, QCheckBox, QDoubleSpinBox, QPushButton, \
    QLabel, QSlider

from segmentation_screen import EventHandler
from segmentation_screen import Events


class ParametersContainer(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        # Timer to load in components before hooking up the corresponding buttons
        self.image_QRadioButton: QRadioButton = None
        self.gradXY_QRadioButton: QRadioButton = None
        self.cellProb_QRadioButton: QRadioButton = None
        self.gradZ_QRadioButton: QRadioButton = None

        self.masksOnCheck_QCheckBox: QCheckBox = None
        self.outlinesOnCheck_QCheckBox: QCheckBox = None

        self.calibrationValue_QDoubleSpinBox: QDoubleSpinBox = None
        self.calibrateButton_QPushButton: QPushButton = None

        self.firstChannel_QComboBox: QComboBox = None
        self.secondChannel_QComboBox: QComboBox = None

        self.flowThresholdValue_QDoubleSpinBox: QDoubleSpinBox = None

        self.cellprobThresholdValue_QDoubleSpinBox: QDoubleSpinBox = None

        self.stitchThresholdValue_QDoubleSpinBox: QDoubleSpinBox = None

        self.model_QComboBox: QComboBox = None
        self.runModel_QPushButton: QPushButton = None

        self.progressBarModel_QProgressBar: QProgressBar = None
        self.roiLabel_QLabel: QLabel = None

        self.autoAdjustImageSaturation_QCheckBox: QCheckBox = None
        self.imageSaturationSlider_QSlider: QSlider = None
        QTimer.singleShot(50, self.setup_ui_elements)

    def setup_ui_elements(self):
        self.image_QRadioButton = self.findChild(QRadioButton, "image_button")
        if self.image_QRadioButton is None:
            print('GUI_INFO: Failed to get the image_QRadioButton')
        self.gradXY_QRadioButton = self.findChild(QRadioButton, "gradxy_button")
        if self.gradXY_QRadioButton is None:
            print('GUI_INFO: Failed to get the gradXY_QRadioButton')
        self.cellProb_QRadioButton = self.findChild(QRadioButton, "cellprob_button")
        if self.cellProb_QRadioButton is None:
            print('GUI_INFO: Failed to get the cellProb_QRadioButton')
        self.gradZ_QRadioButton = self.findChild(QRadioButton, "gradz_button")
        if self.gradZ_QRadioButton is None:
            print('GUI_INFO: Failed to get the gradZ_QRadioButton')

        self.masksOnCheck_QCheckBox = self.findChild(QCheckBox, "masksOnCheck")
        if self.masksOnCheck_QCheckBox is None:
            print('GUI_INFO: Failed to get the masksOnCheck_QCheckBox')
        self.outlinesOnCheck_QCheckBox = self.findChild(QCheckBox, "outlinesOnCheck")
        if self.outlinesOnCheck_QCheckBox is None:
            print('GUI_INFO: Failed to get the outlinesOnCheck_QCheckBox')

        self.calibrationValue_QDoubleSpinBox = self.findChild(QDoubleSpinBox, "calibrationValue")
        if self.calibrationValue_QDoubleSpinBox is None:
            print('GUI_INFO: Failed to get the calibrationValue_QDoubleSpinBox')
        self.calibrateButton_QPushButton = self.findChild(QPushButton, "calibrateButton")
        if self.calibrateButton_QPushButton is None:
            print('GUI_INFO: Failed to get the calibrateButton_QPushButton')

        self.firstChannel_QComboBox = self.findChild(QComboBox, "firstChannel")
        if self.firstChannel_QComboBox is None:
            print('GUI_INFO: Failed to get the firstChannel_QComboBox')
        self.secondChannel_QComboBox = self.findChild(QComboBox, "secondChannel")
        if self.secondChannel_QComboBox is None:
            print('GUI_INFO: Failed to get the secondChannel_QComboBox')

        self.flowThresholdValue_QDoubleSpinBox = self.findChild(QDoubleSpinBox, "flowThresholdValue")
        if self.flowThresholdValue_QDoubleSpinBox is None:
            print('GUI_INFO: Failed to get the flowThresholdValue_QDoubleSpinBox')

        self.cellprobThresholdValue_QDoubleSpinBox = self.findChild(QDoubleSpinBox, "cellprobThresholdValue")
        if self.cellprobThresholdValue_QDoubleSpinBox is None:
            print('GUI_INFO: Failed to get the cellprobThresholdValue_QDoubleSpinBox')

        self.stitchThresholdValue_QDoubleSpinBox = self.findChild(QDoubleSpinBox, "stitchThresholdValue")
        if self.stitchThresholdValue_QDoubleSpinBox is None:
            print('GUI_INFO: Failed to get the stitchThresholdValue_QDoubleSpinBox')

        self.model_QComboBox = self.findChild(QComboBox, "modelName")
        if self.model_QComboBox is None:
            print('GUI_INFO: Failed to get the model_QComboBox')
        self.runModel_QPushButton = self.findChild(QPushButton, "runModelButton")
        if self.runModel_QPushButton is None:
            print('GUI_INFO: Failed to get the runModel_QPushButton')

        self.progressBarModel_QProgressBar = self.findChild(QProgressBar, 'progressBar')
        if self.progressBarModel_QProgressBar is None:
            print('GUI_INFO: Failed to get the progressBarModel_QProgressBar')
        self.roiLabel_QLabel = self.findChild(QLabel, 'roiLabel')
        if self.roiLabel_QLabel is None:
            print('GUI_INFO: Failed to get the roiLabel_QLabel')

        self.autoAdjustImageSaturation_QCheckBox = self.findChild(QCheckBox, "imageSaturationCheckBox")
        if self.autoAdjustImageSaturation_QCheckBox is None:
            print('GUI_INFO: Failed to get the autoAdjustImageSaturation_QCheckBox')
        self.imageSaturationSlider_QSlider = self.findChild(QSlider, "imageSaturationSlider")
        if self.imageSaturationSlider_QSlider is None:
            print('GUI_INFO: Failed to get the imageSaturationSlider_QSlider')

        self.setup_events_for_buttons()

    def setup_events_for_buttons(self):
        self.image_QRadioButton.clicked.connect(lambda: EventHandler().dispatch_event(Events.IMAGE_SELECTED))
        self.gradXY_QRadioButton.clicked.connect(lambda: EventHandler().dispatch_event(Events.GRADXY_SELECTED))
        self.cellProb_QRadioButton.clicked.connect(lambda: EventHandler().dispatch_event(Events.CELLPROB_SELECTED))
        self.gradZ_QRadioButton.clicked.connect(lambda: EventHandler().dispatch_event(Events.GRADZ_SELECTED))
        self.masksOnCheck_QCheckBox.toggled.connect(lambda: EventHandler().dispatch_event(Events.MASKS_ON_TOGGLED))
        self.outlinesOnCheck_QCheckBox.toggled.connect(lambda: EventHandler().dispatch_event(Events.OUTLINES_ON_TOGGLED))
        self.calibrateButton_QPushButton.clicked.connect(lambda: EventHandler().dispatch_event(Events.CALIBRATE_PRESSED))
        self.runModel_QPushButton.clicked.connect(lambda: EventHandler().dispatch_event(Events.RUN_MODEL_PRESSED))
        self.autoAdjustImageSaturation_QCheckBox.toggled.connect(lambda: EventHandler().dispatch_event(Events.AUTO_ADJUST_TOGGLED))
        self.imageSaturationSlider_QSlider.sliderMoved.connect(lambda: EventHandler().dispatch_event(Events.SATURATION_SLIDER_ADJUSTED))
