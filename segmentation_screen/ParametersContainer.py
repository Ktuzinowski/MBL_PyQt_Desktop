from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFrame, QComboBox, QProgressBar, QRadioButton, QCheckBox, QDoubleSpinBox, QPushButton, \
    QLabel, QSlider
from iconify.qt import QtCore
from superqt import QRangeSlider

from segmentation_screen import EventHandler, DisplayEvents
from segmentation_screen import ParameterEvents


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
        self.imageSaturationSlider_QRangeSlider: QRangeSlider = None
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
        self.imageSaturationSlider_QRangeSlider = self.findChild(QSlider, "imageSaturationSlider")
        if self.imageSaturationSlider_QRangeSlider is None:
            print('GUI_INFO: Failed to get the imageSaturationSlider_QSlider')
        self.imageSaturationSlider_QRangeSlider.setMinimum(0)
        self.imageSaturationSlider_QRangeSlider.setMaximum(255)
        self.imageSaturationSlider_QRangeSlider.setValue([0, 255])
        self.imageSaturationSlider_QRangeSlider.setTickPosition(QSlider.TicksRight)
        self.setup_events_for_buttons()

        self.model_QComboBox.currentIndexChanged.connect(self.update_value_for_current_model)
        self.firstChannel_QComboBox.currentIndexChanged.connect(self.update_value_for_first_channel)
        self.secondChannel_QComboBox.currentIndexChanged.connect(self.update_value_for_second_channel)
        self.flowThresholdValue_QDoubleSpinBox.valueChanged.connect(self.update_for_flow_threshold_change)
        self.cellprobThresholdValue_QDoubleSpinBox.valueChanged.connect(self.update_for_cellprob_change)

        # Events from DisplayContainer
        EventHandler().add_event_listener(DisplayEvents.AUTO_ADJUST_SATURATION_SLIDER, self.adjust_max_min_values_for_slider)
        EventHandler().add_event_listener(DisplayEvents.CALIBRATED_FOR_CELL_DIAMETER, self.update_cell_diameter)
        EventHandler().add_event_listener(DisplayEvents.FINISHED_SEGMENTATION, self.update_parameters_for_segmentation)
        EventHandler().add_event_listener(DisplayEvents.RESET_FOR_NEW_IMAGE, self.reset_for_new_image)

    def setup_events_for_buttons(self):
        self.image_QRadioButton.clicked.connect(lambda: self.update_view_and_event_for_image_selected())
        self.gradXY_QRadioButton.clicked.connect(lambda: self.update_view_and_event_for_gradXY_selected())
        self.cellProb_QRadioButton.clicked.connect(lambda: self.update_view_and_event_for_cellProb_selected())
        self.gradZ_QRadioButton.clicked.connect(lambda: self.update_view_and_event_for_gradZ_selected())
        self.masksOnCheck_QCheckBox.toggled.connect(lambda: self.handle_event_for_toggled_mask())
        self.outlinesOnCheck_QCheckBox.toggled.connect(lambda: self.handle_event_for_toggled_outlines())
        self.calibrateButton_QPushButton.clicked.connect(lambda: EventHandler().dispatch_event(ParameterEvents.CALIBRATE_PRESSED))
        self.runModel_QPushButton.clicked.connect(lambda: EventHandler().dispatch_event(ParameterEvents.RUN_MODEL_PRESSED))
        self.autoAdjustImageSaturation_QCheckBox.toggled.connect(lambda: EventHandler().dispatch_event(ParameterEvents.AUTO_ADJUST_TOGGLED))
        self.imageSaturationSlider_QRangeSlider.valueChanged.connect(lambda: self.handle_saturation_value_adjusted())

    def reset_for_new_image(self):
        self.roiLabel_QLabel.setText(f"{EventHandler().rois} ROIs")
        self.progressBarModel_QProgressBar.setValue(0)

    def update_view_and_event_for_image_selected(self):
        EventHandler().current_view = 0
        EventHandler().dispatch_event(ParameterEvents.IMAGE_SELECTED)

    def update_view_and_event_for_gradXY_selected(self):
        EventHandler().current_view = 1
        EventHandler().dispatch_event(ParameterEvents.GRADXY_SELECTED)
    def update_view_and_event_for_cellProb_selected(self):
        EventHandler().current_view = 2
        EventHandler().dispatch_event(ParameterEvents.CELLPROB_SELECTED)

    def update_view_and_event_for_gradZ_selected(self):
        EventHandler().current_view = 3
        EventHandler().dispatch_event(ParameterEvents.GRADZ_SELECTED)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_X:
            if self.masksOnCheck_QCheckBox.isChecked():
                self.masksOnCheck_QCheckBox.setChecked(False)
            else:
                self.masksOnCheck_QCheckBox.setChecked(True)
            self.handle_event_for_toggled_mask()
        elif event.key() == QtCore.Qt.Key_Z:
            if self.outlinesOnCheck_QCheckBox.isChecked():
                self.outlinesOnCheck_QCheckBox.setChecked(False)
            else:
                self.outlinesOnCheck_QCheckBox.setChecked(True)
            self.handle_event_for_toggled_outlines()

    def handle_event_for_toggled_mask(self):
        EventHandler().masks_on = self.masksOnCheck_QCheckBox.isChecked()
        EventHandler().dispatch_event(ParameterEvents.MASKS_ON_TOGGLED)

    def handle_event_for_toggled_outlines(self):
        EventHandler().outlines_on = self.outlinesOnCheck_QCheckBox.isChecked()
        EventHandler().dispatch_event(ParameterEvents.OUTLINES_ON_TOGGLED)

    def update_for_cellprob_change(self):
        EventHandler().cellprob_threshold = self.cellprobThresholdValue_QDoubleSpinBox.value()

    def update_for_flow_threshold_change(self):
        EventHandler().flow_threshold = self.flowThresholdValue_QDoubleSpinBox.value()

    def handle_saturation_value_adjusted(self):
        sval = self.imageSaturationSlider_QRangeSlider.value()
        EventHandler().saturation_value_min = sval[0]
        EventHandler().saturation_value_max = sval[1]
        EventHandler().dispatch_event(ParameterEvents.SATURATION_SLIDER_ADJUSTED)

    def update_value_for_current_model(self):
        EventHandler().current_model = self.model_QComboBox.currentText().lower()

    def update_value_for_first_channel(self):
        EventHandler().first_channel = self.firstChannel_QComboBox.currentIndex()

    def update_value_for_second_channel(self):
        EventHandler().second_channel = self.secondChannel_QComboBox.currentIndex()

    def update_cell_diameter(self):
        self.calibrationValue_QDoubleSpinBox.setValue(EventHandler().cell_diameter)

    def adjust_max_min_values_for_slider(self):
        self.imageSaturationSlider_QRangeSlider.setValue([EventHandler().saturation_value_min, EventHandler().saturation_value_max])

    def update_parameters_for_segmentation(self):
        self.roiLabel_QLabel.setText(f"{EventHandler().rois} ROIs")
        self.progressBarModel_QProgressBar.setValue(100)
        self.masksOnCheck_QCheckBox.setChecked(True)
