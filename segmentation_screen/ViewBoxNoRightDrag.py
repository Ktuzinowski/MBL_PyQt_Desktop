import pyqtgraph as pg


class ViewBoxNoRightDrag(pg.ViewBox):
    def __init__(self, parent=None, border=None, lock_aspect=False, enable_mouse=True, invert_y=False, enable_menu=True,
                 name=None, invert_x=False):
        pg.ViewBox.__init__(self, None, border, lock_aspect, enable_mouse, invert_y, enable_menu, name, invert_x)
        self.parent = parent
        self.axHistoryPointer = -1

    def keyPressEvent(self, ev):
        """
        This routine should capture key presses in the current view box.
        The following events are implemented:
        +/= : moves forward in the zooming stack (if it exists)
        - : moves backward in the zooming stack (if it exists)
        """
        ev.accept()
        if ev.text() == '-':
            self.scaleBy([1.1, 1.1])
        elif ev.text() in ['+', '=']:
            self.scaleBy([0.9, 0.9])
        else:
            ev.ignore()
