from PyQt5 import QtCore
import functools


@functools.lru_cache()
class GlobalObject(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self._events = {}
        self.data_frame = None
        self.num_components = 0
        self.verbose = 0
        self.perplexity = 0
        self.num_iterations = 0

    def add_event_listener(self, name, func):
        if name not in self._events:
            self._events[name] = [func]
        else:
            self._events[name].append(func)

    def dispatch_event(self, name):
        functions = self._events.get(name, [])
        for func in functions:
            QtCore.QTimer.singleShot(0, func)
