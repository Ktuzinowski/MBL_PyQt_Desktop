import pyqtgraph as pg
import numpy as np
from segmentation_screen import EventHandler
from qtpy import QtCore


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

    def mouseClickEvent(self, ev):
        y, x = int(ev.pos().y()), int(ev.pos().x())
        print(y, x)
        if 0 <= y < self.parent.Ly and 0 <= x < self.parent.Lx:
            if ev.button() == QtCore.Qt.LeftButton and not ev.double():
                idx = self.parent.cell_pixel[self.parent.currentZ][y, x]
                if idx > 0:
                    if EventHandler().masks_on:
                        self.parent.unselect_cell()
                        self.parent.select_cell(idx)
                elif EventHandler().masks_on:
                    self.parent.unselect_cell()

