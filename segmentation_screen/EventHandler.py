from PyQt5 import QtCore
import functools
from segmentation_screen import Channels
from segmentation_screen import Models


@functools.lru_cache()
class EventHandler(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self._events = {}
        self.image_mode = "IMAGE_SELECTED"
        self.masks_on = True
        self.outlines_on = False
        self.cell_diameter = 30.0
        self.current_model: Models = Models.CYTO2
        self.first_channel: Channels = Channels.GRAY
        self.second_channel: Channels = Channels.NONE

        self.flow_threshold = 0.0
        self.cellprob_threshold = 0.4
        self.stitch_threshold = 0.0

        self.rois = 0
        self.progress_value = 0
        self.auto_adjust = True
        self.saturation_value_min = 0
        self.saturation_value_max = 0

    def add_event_listener(self, name, func):
        if name not in self._events:
            self._events[name] = [func]
        else:
            self._events[name].append(func)

    def dispatch_event(self, name):
        functions = self._events.get(name, [])
        for func in functions:
            QtCore.QTimer.singleShot(0, func)
