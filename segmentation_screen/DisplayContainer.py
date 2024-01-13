import datetime
import os
import gc
from tqdm import trange
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QFileDialog
from cellpose.io import imread
from cellpose.plot import disk
from cellpose import models
from qtpy import QtCore

from segmentation_screen import EventHandler, make_spectral, make_cmap
from segmentation_screen import ParameterEvents
from segmentation_screen import DisplayEvents
from segmentation_screen import ImageDraw
from segmentation_screen import ViewBoxNoRightDrag
from segmentation_screen import make_bwr


class DisplayContainer(QFrame):

    def __init__(self, parent=None):
        super(DisplayContainer, self).__init__(parent)
        self.model = None
        self.current_model_path = None
        self.current_model = None
        self.one_channel = False
        self.pOrtho = None
        self.imgOrtho = None
        self.layerOrtho = None
        self.filename = None
        self.cmap = None
        self.training_params = None
        self.is_stack = None
        self.colormap = None
        self.bwr = None
        self.hLineOrtho = None
        self.vLineOrtho = None
        self.scale = None
        self.layer = None
        self.image = None
        self.cursorCross = None
        self.brush_size = 3
        self.view = 0  # 0=image, 1=flowsXY, 2=flowsZ, 3=cellprob

        # -- zero out image stack -- #
        self.opacity = 128  # how opaque masks should be
        self.out_color = [200, 200, 255, 200]
        self.NZ, self.Ly, self.Lx = 1, 512, 512
        self.saturation = [[0, 255] for n in range(self.NZ)]
        self.currentZ = 0
        self.flows = [[], [], [], [], [[]]]
        self.stack = np.zeros((1, self.Ly, self.Lx, 3))
        # masks matrix
        self.layerz = 0 * np.ones((self.Ly, self.Lx, 4), np.uint8)
        # image matrix with a scale disk
        self.radii = 0 * np.ones((self.Ly, self.Lx, 4), np.uint8)
        self.cell_pixel = np.zeros((1, self.Ly, self.Lx), np.uint32)
        self.out_pixel = np.zeros((1, self.Ly, self.Lx), np.uint32)
        self.is_manual = np.zeros(0, 'bool')
        self.filename = []
        self.loaded = False
        self.recompute_masks = False
        self.deleting_multiple = False
        self.removing_cells_list = []
        self.removing_region = False
        self.remove_roi_object = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        # image viewer
        pg.setConfigOptions(imageAxisOrder="row-major")
        self.win = pg.GraphicsLayoutWidget()
        main_layout.addWidget(self.win)
        self.win.scene().sigMouseClicked.connect(self.plot_clicked)
        self.win.scene().sigMouseMoved.connect(self.mouse_moved)
        self.make_viewbox()
        self.make_orthoviews()

        bwr_map = make_bwr()
        self.bwr = bwr_map.getLookupTable(start=0.0, stop=255.0, alpha=False)
        self.cmap = []
        # spectral colormap
        self.cmap.append(make_spectral().getLookupTable(start=0.0, stop=255.0, alpha=False))
        # single channel colormaps
        for i in range(3):
            self.cmap.append(make_cmap(i).getLookupTable(start=0.0, stop=255.0, alpha=False))

        np.random.seed(42)  # make colors stable
        self.colormap = ((np.random.rand(1000000, 3) * 0.8 + 0.1) * 255).astype(np.uint8)
        self.is_stack = True  # always loading images of same FOV
        d = datetime.datetime.now()
        self.training_params = {
            'model_index': 0,
            'learning_rate': 0.1,
            'weight_decay': 0.0001,
            'n_epochs': 100,
            'model_name': 'CP' + d.strftime("_%Y%m%d_%H%M%S")
        }
        self.setAcceptDrops(True)
        self.win.show()

        EventHandler().add_event_listener(ParameterEvents.IMAGE_SELECTED, self.image_selected)
        EventHandler().add_event_listener(ParameterEvents.GRADXY_SELECTED, self.gradxy_selected)
        EventHandler().add_event_listener(ParameterEvents.CELLPROB_SELECTED, self.cellprob_selected)
        EventHandler().add_event_listener(ParameterEvents.GRADZ_SELECTED, self.gradz_selected)
        EventHandler().add_event_listener(ParameterEvents.MASKS_ON_TOGGLED, self.handle_masks_toggled)
        EventHandler().add_event_listener(ParameterEvents.OUTLINES_ON_TOGGLED, self.handle_outlines_toggled)
        EventHandler().add_event_listener(ParameterEvents.CALIBRATE_PRESSED, self.handle_calibration_button)
        EventHandler().add_event_listener(ParameterEvents.RUN_MODEL_PRESSED, self.handle_run_model_pressed)
        EventHandler().add_event_listener(ParameterEvents.AUTO_ADJUST_TOGGLED, self.handle_auto_adjust_toggled)
        EventHandler().add_event_listener(ParameterEvents.SATURATION_SLIDER_ADJUSTED,
                                          self.handle_saturation_slider_adjusted)

        self.setLayout(main_layout)

    def make_viewbox(self):
        self.cursorCross = ViewBoxNoRightDrag(
            parent=self,
            lock_aspect=True,
            name='cursorCross',
            border=[0, 0, 0],
            invert_y=True
        )
        self.cursorCross.setCursor(QtCore.Qt.CrossCursor)
        self.win.addItem(self.cursorCross, 0, 0, rowspan=1, colspan=1)
        self.cursorCross.setMenuEnabled(False)
        self.cursorCross.setMouseEnabled(x=True, y=True)
        self.image = pg.ImageItem(viewbox=self.cursorCross, parent=self)
        self.image.autoDownsample = False
        self.layer = ImageDraw(view_box=self.cursorCross, parent=self)
        self.layer.setLevels([0, 255])
        self.scale = pg.ImageItem(viewbox=self.cursorCross, parent=self)
        self.scale.setLevels([0, 255])
        self.cursorCross.scene().contextMenuItem = self.cursorCross
        self.Ly, self.Lx = 512, 512
        self.cursorCross.addItem(self.image)
        self.cursorCross.addItem(self.layer)
        self.cursorCross.addItem(self.scale)

    def make_orthoviews(self):
        self.pOrtho, self.imgOrtho, self.layerOrtho = [], [], []
        for j in range(2):
            self.pOrtho.append(pg.ViewBox(
                lockAspect=True,
                name=f'plotOrtho{j}',
                border=[0, 0, 0],
                invertY=True,
                enableMouse=False
            ))
            self.pOrtho[j].setMenuEnabled(False)

            self.imgOrtho.append(pg.ImageItem(viewbox=self.pOrtho[j], parent=self))
            self.imgOrtho[j].autoDownsample = False

            self.layerOrtho.append(pg.ImageItem(viewbox=self.pOrtho[j], parent=self))
            self.layerOrtho[j].setLevels([0, 255])

            self.vLineOrtho = [pg.InfiniteLine(angle=90, movable=False), pg.InfiniteLine(angle=90, movable=False)]
            self.hLineOrtho = [pg.InfiniteLine(angle=0, movable=False), pg.InfiniteLine(angle=0, movable=False)]

            self.pOrtho[j].addItem(self.imgOrtho[j])
            self.pOrtho[j].addItem(self.layerOrtho[j])
            self.pOrtho[j].addItem(self.vLineOrtho[j], ignoreBounds=False)
            self.pOrtho[j].addItem(self.hLineOrtho[j], ignoreBounds=False)

        self.pOrtho[0].linkView(self.pOrtho[0].YAxis, self.cursorCross)
        self.pOrtho[1].linkView(self.pOrtho[1].XAxis, self.cursorCross)

    def plot_clicked(self):
        print('clicking inside of viewing plot')

    def mouse_moved(self):
        if False:
            print('mouse moved')

    def image_selected(self):
        print('IMAGE_SELECTED EVENT!')

    def gradxy_selected(self):
        print('GRADXY_SELECTED EVENT!')

    def cellprob_selected(self):
        print('CELLPROB_SELECTED EVENT!')

    def gradz_selected(self):
        print('GRADZ_SELECTED EVENT!')

    def handle_masks_toggled(self):
        print(ParameterEvents.MASKS_ON_TOGGLED)

    def handle_outlines_toggled(self):
        print(ParameterEvents.OUTLINES_ON_TOGGLED)

    def handle_calibration_button(self):
        self.initialize_model(model_name='cyto')
        diameters, _ = self.model.sz.eval(self.stack[self.currentZ].copy(),
                                          channels=self.get_channels(), progress=None)
        print('GUI_INFO: Estimated diameter of cells using %s model = %0.1f pixels' % (self.current_model, diameters))
        EventHandler().cell_diameter = diameters
        EventHandler().dispatch_event(DisplayEvents.CALIBRATED_FOR_CELL_DIAMETER)
        self.compute_scale()
        print(ParameterEvents.CALIBRATE_PRESSED)

    def get_channels(self):
        channels = [int(EventHandler().first_channel), int(EventHandler().second_channel)]
        if self.current_model == 'nuclei':
            channels[1] = 0
        return channels

    def initialize_model(self, model_name=None):
        if model_name is None and not isinstance(model_name, str):
            self.get_model_path()
            self.model = models.CellposeModel(gpu=False, pretrained_model=self.current_model_path)
        else:
            self.current_model = model_name
            if 'cyto' in self.current_model or 'nuclei' in self.current_model:
                self.current_model_path = models.model_path(self.current_model, 0)
            else:
                self.current_model_path = os.fspath(models.MODEL_DIR.joinpath(self.current_model))
            if self.current_model == 'cyto':
                self.model = models.Cellpose(gpu=False, model_type=self.current_model)
            else:
                self.model = models.CellposeModel(gpu=False, model_type=self.current_model)

    def get_model_path(self):
        self.current_model = EventHandler().current_model
        self.current_model_path = os.fspath(models.MODEL_DIR.joinpath(self.current_model))

    def handle_run_model_pressed(self):
        print(ParameterEvents.RUN_MODEL_PRESSED)

    def handle_auto_adjust_toggled(self):
        print(ParameterEvents.AUTO_ADJUST_TOGGLED)

    def handle_saturation_slider_adjusted(self):
        min_saturation = EventHandler().saturation_value_min
        max_saturation = EventHandler().saturation_value_max
        sval = (min_saturation, max_saturation)
        if self.loaded:
            self.saturation[self.currentZ] = sval
            if not EventHandler().auto_adjust:
                for i in range(len(self.saturation)):
                    self.saturation[i] = sval
            self.update_plot()
        print(ParameterEvents.SATURATION_SLIDER_ADJUSTED)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [x.toLocalFile() for x in event.mimeData().urls()]
        print(files)
        self.load_image(filename=files[0])

    def load_image(self, filename=None, load_seg=True):
        """ load image with filename, if None, open QFileDialog """
        if filename is None:
            name = QFileDialog.getOpenFileName(
                self, "Load Image"
            )
            filename = name[0]
        else:
            print('GUI_INFO: filename is not none')
        try:
            print(f'GUI_INFO: loading image: {filename}')
            image = imread(filename)
            self.loaded = True
        except Exception as e:
            print('ERROR: images not compatible')
            print(f'ERROR: {e}')

        if self.loaded:
            self.filename = filename
            print('GUI_INFO: filename info:', self.filename)
            self.initialize_images(image)

    def initialize_images(self, image):
        """ format image for GUI """
        print('GUI_INFO: Image shape:', image.shape)
        self.one_channel = False
        if image.ndim > 3:
            # make tiff Z x channels x W x H
            print('GUI_INFO: image has greater than 3 dimensions')
            if image.shape[0] < 4:
                # tiff is channels x Z x W x H
                image = np.transpose(image, (1, 0, 2, 3))
                print('GUI_INFO: tiff is channels x Z x W x H')
            elif image.shape[-1] < 4:
                # tiff is Z x W x H x channels
                image = np.transpose(image, (0, 3, 1, 2))
                print('GUI_INFO: tiff is Z x W x H x channels')
            # fill in with blank channels to make 3 channels
            if image.shape[1] < 3:
                shape = image.shape
                image = np.concatenate((image, np.zeros((shape[0], 3 - shape[1], shape[2], shape[3]), dtype=np.uint8)),
                                       axis=1)
                if 3 - shape[1] > 1:
                    self.one_channel = True
                    np.transpose(image, (0, 2, 3, 1))
        elif image.ndim == 3:
            if image.shape[0] < 5:
                image = np.transpose(image, (1, 2, 0))
            if image.shape[-1] < 3:
                shape = image.shape
                image = np.concatenate(
                    (image, np.zeros((shape[0], shape[1], 3 - shape[2]), dtype=type(image[0, 0, 0]))), axis=-1)
                if 3 - shape[2] > 1:
                    self.one_channel = True
                image = image[np.newaxis, ...]
            elif 5 > image.shape[-1] > 2:
                image = image[:, :, :3]
                image = image[np.newaxis, ...]
        else:
            image = image[np.newaxis, ...]

        image_min = image.min()
        image_max = image.max()
        print('GUI_INFO: Image min:', image_min, "Image max:", image_max)
        self.stack = image
        self.stack = self.stack.astype(np.float32)
        self.stack -= image_min
        # Max-Min Normalization of Image
        if image_max > image_min + 1e-3:
            self.stack /= (image_max - image_min)
        self.stack *= 255
        del image
        gc.collect()

        if self.stack.ndim < 4:
            print('GUI_INFO: Stack dimensions are less than 4')
            self.one_channel = True
            self.stack = self.stack[:, :, :, np.newaxis]

        self.Ly, self.Lx = self.stack.shape[1:3]
        self.layerz = 255 * np.ones((self.Ly, self.Lx, 4), 'uint8')
        print(self.layerz.shape)
        # maybe we need to compute saturation
        if EventHandler().auto_adjust:
            self.compute_saturation()
        if len(self.saturation) != self.NZ:
            self.saturation = []
            for n in range(self.NZ):
                self.saturation.append([0, 255])

        self.compute_scale()
        self.currentZ = int(np.floor(self.NZ / 2))

    def compute_scale(self):
        diameter = EventHandler().cell_diameter
        pr = int(float(diameter))
        radii_padding = int(pr * 1.25)
        self.radii = np.zeros((self.Ly + radii_padding, self.Lx, 4), np.uint8)
        yy, xx = disk([self.Ly + radii_padding / 2 - 1, pr / 2 + 1], pr / 2, self.Ly + radii_padding, self.Lx)
        self.radii[yy, xx, 0] = 150
        self.radii[yy, xx, 1] = 50
        self.radii[yy, xx, 2] = 150
        self.radii[yy, xx, 3] = 255
        self.update_plot()
        self.cursorCross.setYRange(0, self.Ly + radii_padding)
        self.cursorCross.setXRange(0, self.Lx)
        self.win.show()

    def update_plot(self):
        self.Ly, self.Lx, _ = self.stack[self.currentZ].shape
        if self.view == 0:
            image = self.stack[self.currentZ]
            if self.one_channel:
                # show single channel
                image = self.stack[self.currentZ, :, :, 0]
            self.image.setImage(image, autoLevels=False, lut=None)
            self.image.setLevels(self.saturation[self.currentZ])
            self.image.setLevels(self.saturation[self.currentZ])
        else:
            image = np.zeros((self.Ly, self.Lx), np.uint8)
            if len(self.flows) >= self.view - 1 and len(self.flows[self.view - 1]) > 0:
                image = self.flows[self.view - 1][self.currentZ]
            if self.view > 1:
                self.image.setImage(image, autoLevels=False, lut=self.bwr)
            else:
                self.image.setImage(image, autoLevels=False, lut=self.bwr)
            self.image.setLevels([0.0, 255.0])
        self.scale.setImage(self.radii, autoLevels=False)
        self.scale.setLevels([0.0, 255.0])
        # potentially update ortho
        self.win.show()

    def compute_saturation(self):
        # compute percentiles from stack
        self.saturation = []
        print('GUI_INFO: auto-adjust enabled, computing saturation levels')
        if self.NZ > 10:
            iterator = trange(self.NZ)
        else:
            iterator = range(self.NZ)
        for n in iterator:
            min_value = np.percentile(self.stack[n].astype(np.float32), 1)
            max_value = np.percentile(self.stack[n].astype(np.float32), 99)
            EventHandler().saturation_value_min = min_value
            EventHandler().saturation_value_max = max_value
            print('MIN_VALUE:', min_value, "MAX_VALUE:", max_value)
            EventHandler().dispatch_event(DisplayEvents.AUTO_ADJUST_SATURATION_SLIDER)
            self.saturation.append([np.percentile(self.stack[n].astype(np.float32), 1),
                                    np.percentile(self.stack[n].astype(np.float32), 99)])
