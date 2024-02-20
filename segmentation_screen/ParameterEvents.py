from enum import Enum


class ParameterEvents(Enum):
    IMAGE_SELECTED = "IMAGE_SELECTED"
    GRADXY_SELECTED = "GRADXY_SELECTED"
    CELLPROB_SELECTED = "CELLPROB_SELECTED"
    GRADZ_SELECTED = "GRADZ_SELECTED"
    MASKS_ON_TOGGLED = "MASKS_ON_TOGGLED"
    OUTLINES_ON_TOGGLED = "OUTLINES_ON_TOGGLED"
    CALIBRATE_PRESSED = "CALIBRATE_PRESSED"
    RUN_MODEL_PRESSED = "RUN_MODEL_PRESSED"
    AUTO_ADJUST_TOGGLED = "AUTO_ADJUST_TOGGLED"
    SATURATION_SLIDER_ADJUSTED = "SATURATION_SLIDER_ADJUSTED"
    UPDATE_CALIBRATION_DISK = "UPDATE_CALIBRATION_DISK"
    UPDATE_PROTEIN_SIGNAL_LAYER = "UPDATE_PROTEIN_SIGNAL_LAYER"
