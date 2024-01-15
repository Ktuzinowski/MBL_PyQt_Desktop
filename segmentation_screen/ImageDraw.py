import pyqtgraph as pg
from qtpy import QtCore
import numpy as np


class ImageDraw(pg.ImageItem):
    def __init__(self, image=None, view_box=None, parent=None, **other_args):
        super(ImageDraw, self).__init__()
        self.scatter = None
        self.levels = np.array([0, 255])
        self.lut = None
        self.autoDownsample = False
        self.axisOrder = 'row-major'
        self.removable = False

        self.parent = parent
