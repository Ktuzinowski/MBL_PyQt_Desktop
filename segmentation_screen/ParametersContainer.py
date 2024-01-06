from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFrame, QPushButton, QDoubleSpinBox, QComboBox, QProgressBar
import numpy as np
import os
from cellpose import models


class ParametersContainer(QFrame):
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
        diameter, _ = self.model.sz.eval(self.stack[self.currentZ].copy(), channels=self.get_channels(),
                                         progress=self.progress)
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
