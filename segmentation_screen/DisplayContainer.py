import datetime
import os
import gc
import time

import cv2
import fastremap
from tqdm import trange
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QFileDialog
from cellpose.io import imread
from cellpose.plot import disk
from cellpose import models
from cellpose import utils
from cellpose.transforms import normalize99, resize_image
from qtpy import QtCore

from segmentation_screen import EventHandler, make_spectral, make_cmap
from segmentation_screen import ParameterEvents
from segmentation_screen import DisplayEvents
from segmentation_screen import ImageDraw
from segmentation_screen import ViewBoxNoRightDrag
from segmentation_screen import make_bwr
from main_screen import SegmentationMenuEvents
import imageio


class DisplayContainer(QFrame):

    def __init__(self, parent=None):
        super(DisplayContainer, self).__init__(parent)
        # Original masks to base off of
        self.masks = None
        self.removed_cell = None
        self.selected = 0
        self.prev_selected = 0
        self.layer_off = False
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
        self.filename = []
        self.loaded = False
        self.recompute_masks = False
        self.deleting_multiple = False
        self.removing_cells_list = []
        self.removing_region = False
        self.remove_roi_object = None
        self.cell_colors = np.array([255, 255, 255])[np.newaxis, :]
        self.strokes = []
        self.track_changes = []

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
        EventHandler().add_event_listener(ParameterEvents.UPDATE_CALIBRATION_DISK, self.compute_scale)

        # Main Menu Events
        EventHandler().add_event_listener(SegmentationMenuEvents.LOAD_IMAGE, self.handle_segmentation_menu_load_image)
        EventHandler().add_event_listener(SegmentationMenuEvents.SAVE_MASKS_FOR_MULTILAYER_TIFF, self.handle_segmentation_menu_save_masks_tiff)
        EventHandler().add_event_listener(SegmentationMenuEvents.SAVE_OUTLINES_FOR_MULTILAYER_TIFF, self.handle_segmentation_menu_save_outlines_tiff)
        EventHandler().add_event_listener(SegmentationMenuEvents.SAVE_MASKS_AND_OUTLINES_FOR_MULTILAYER_TIFF, self.handle_segmentation_menu_save_masks_and_outlines_tiff)
        EventHandler().add_event_listener(SegmentationMenuEvents.SAVE_MASKS_ONLY_NPY, self.handle_segmentation_menu_masks_only_npy)
        EventHandler().add_event_listener(SegmentationMenuEvents.SAVE_OUTLINES_ONLY_NPY, self.handle_segmentation_menu_outlines_only_npy)
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
        self.update_view_from_radio_buttons()

    def gradxy_selected(self):
        self.update_view_from_radio_buttons()

    def cellprob_selected(self):
        self.update_view_from_radio_buttons()

    def gradz_selected(self):
        self.update_view_from_radio_buttons()

    def update_view_from_radio_buttons(self):
        self.view = EventHandler().current_view
        if self.loaded:
            self.update_plot()

    def handle_masks_toggled(self):
        self.remove_or_add_masks_and_outlines()
        print(ParameterEvents.MASKS_ON_TOGGLED)

    def handle_outlines_toggled(self):
        self.remove_or_add_masks_and_outlines()
        print(ParameterEvents.OUTLINES_ON_TOGGLED)

    def remove_or_add_masks_and_outlines(self):
        print(EventHandler().masks_on, EventHandler().outlines_on)
        if not EventHandler().masks_on and not EventHandler().outlines_on:
            print('GUI_INFO: REMOVING A LAYER INSIDE OF HERE')
            self.cursorCross.removeItem(self.layer)
            self.layer_off = True
        else:
            if self.layer_off:
                print('GUI_INFO: Adding back the layer')
                self.cursorCross.addItem(self.layer)
            self.draw_layer()
            self.update_layer()
        if self.loaded:
            print('GUI_INFO: Updating for toggling outlines and masks')
            self.update_plot()
            self.update_layer()

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

    def get_thresholds(self):
        try:
            flow_thresholds = float(EventHandler().flow_threshold)
            cellprob_thresholds = float(EventHandler().cellprob_threshold)
            if flow_thresholds == 0.0 or self.NZ < 1:
                flow_thresholds = None
            return flow_thresholds, cellprob_thresholds
        except Exception as e:
            print('Flow Threshold or Cellprob Threshold not a valid number, setting to defaults')
            # TODO: trigger an event to reset the values in the ParametersContainer
            return 0.4, 0.0

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
        self.compute_model()
        EventHandler().dispatch_event(DisplayEvents.FINISHED_SEGMENTATION)
        print(ParameterEvents.RUN_MODEL_PRESSED)

    def handle_auto_adjust_toggled(self):
        print(ParameterEvents.AUTO_ADJUST_TOGGLED)

    def compute_model(self):
        # set progress bar to 0
        try:
            tic = time.time()
            self.clear_all()
            self.flows = [[], [], []]
            self.initialize_model(EventHandler().current_model)
            print('GUI_INFO: INITIALIZING MODEL CORRECTLY')
            do_3D = False
            stitch_threshold = False
            if self.NZ > 1:
                stitch_threshold = float(EventHandler().stitch_threshold)
                print('GUI_INFO: Computing model for 3D with stitch threshold', stitch_threshold)
                stitch_threshold = 0 if stitch_threshold <= 0 or stitch_threshold > 1 else stitch_threshold
                do_3D = True if stitch_threshold == 0 else False
                data = self.stack.copy()
            else:
                data = self.stack[0].copy()
            channels = self.get_channels()
            flow_threshold, cellprob_threshold = self.get_thresholds()
            cell_diameter = float(EventHandler().cell_diameter)
            try:
                masks, flows = self.model.eval(data,
                                               channels=channels,
                                               diameter=cell_diameter,
                                               cellprob_threshold=cellprob_threshold,
                                               flow_threshold=flow_threshold,
                                               do_3D=do_3D,
                                               stitch_threshold=stitch_threshold,
                                               progress=None)[:2]
            except Exception as e:
                print('NET ERROR: %s' % e)
                # set progress bar to value of 0
                return

            # TODO: set progress bar to 75
            self.flows[0] = flows[0].copy()
            self.flows[1] = (np.clip(normalize99(flows[2].copy()), 0, 1) * 255).astype(np.uint8)  # dist/prob
            if not do_3D and not stitch_threshold > 0:
                masks = masks[np.newaxis, ...]
                self.flows[0] = resize_image(self.flows[0], masks.shape[-2], masks.shape[-1],
                                             interpolation=cv2.INTER_NEAREST)
                self.flows[1] = resize_image(self.flows[1], masks.shape[-2], masks.shape[-1])
            if not do_3D and not stitch_threshold > 0:
                self.flows[2] = np.zeros(masks.shape[1:], dtype=np.uint8)
                self.flows = [self.flows[n][np.newaxis, ...] for n in range(len(self.flows))]
            else:
                self.flows[2] = (flows[1][0] / 10 * 127 + 127).astype(np.uint8)
            if len(flows) > 2:
                self.flows.append(flows[3].squeeze())  # p
                self.flows.append(np.concatenate((flows[1], flows[2][np.newaxis, ...]), axis=0))  # dP, dist/prob
            print('%d cells found with model in %0.3f sec' % (len(np.unique(masks)[1:]), time.time() - tic))
            # set progress bar to 80
            # turn on masks
            EventHandler().masks_on = True
            # set progress to 100 after

            if not do_3D and not stitch_threshold > 0:
                self.recompute_masks = True
            else:
                self.recompute_masks = False
            self.masks_to_gui(masks, outlines=None)
        except Exception as e:
            print('ERROR IN COMPUTE_MODEL')
            print('ERROR: %s' % e)

    def masks_to_gui(self, masks, outlines=None):
        """ masks loaded into GUI """
        shape = masks.shape
        print("Shape of masks", shape)
        masks = masks.flatten()
        print("Flattened masks", masks)
        fastremap.renumber(masks, in_place=True)
        print("Renumbered masks in place", masks)
        masks = masks.reshape(shape)
        print("Reshaped masks back to original shape", masks)
        masks = masks.astype(np.uint16) if masks.max() < 2 ** 16 - 1 else masks.astype(np.uint32)
        print("Masks after changing type to either 16 or 32 bit", masks)
        self.cell_pixel = masks
        self.masks = masks
        if self.cell_pixel.ndim == 2:
            self.cell_pixel = self.cell_pixel[np.newaxis, :, :]
        print(f'GUI_INFO: {masks.max()} masks found')

        # get outlines
        if outlines is None:  # parent.outlinesOn
            self.out_pixel = np.zeros_like(masks)
            for z in range(self.NZ):
                print('GUI_INFO: Creating the outlines for the mask')
                outlines = utils.masks_to_outlines(masks[z])
                self.out_pixel[z] = outlines * masks[z]
                if z % 50 == 0 and self.NZ > 1:
                    print('GUI_INFO: plane %d outlines processed' % z)
        else:
            self.out_pixel = outlines
            shape = self.out_pixel.shape
            _, self.out_pixel = np.unique(self.out_pixel, return_inverse=True)
            self.out_pixel = np.reshape(self.out_pixel, shape)

        EventHandler().rois = self.cell_pixel.max()
        colors = self.colormap[:EventHandler().rois, :3]
        print('GUI_INFO: creating cell colors and drawing masks')
        self.cell_colors = np.concatenate((np.array([[255, 255, 255]]), colors), axis=0).astype(np.uint8)
        self.remove_masks_that_do_not_fall_in_range()
        np.save('masks_file.npy', self.cell_pixel)
        self.draw_layer()
        self.update_layer()
        self.update_plot()

    def draw_layer(self):
        if EventHandler().masks_on:
            self.layerz = np.zeros((self.Ly, self.Lx, 4), np.uint8)
            self.layerz[..., :3] = self.cell_colors[self.cell_pixel[self.currentZ], :]
            self.layerz[..., 3] = self.opacity * (self.cell_pixel[self.currentZ] > 0).astype(np.uint8)
            if EventHandler().image_mode > 0:
                self.layerz[self.cell_pixel[self.currentZ] == EventHandler().image_mode] = np.array(
                    [255, 255, 255, self.opacity])
            cZ = self.currentZ
            stroke_z = np.array([s[0][0] for s in self.strokes])
            inZ = np.nonzero(stroke_z == cZ)[0]
            if len(inZ) > 0:
                for i in inZ:
                    stroke = np.array(self.strokes[i])
                    self.layerz[stroke[:, 1], stroke[:, 2]] = np.array([255, 0, 255, 100])
        else:
            self.layerz[..., 3] = 0

        if EventHandler().outlines_on:
            self.layerz[self.out_pixel[self.currentZ] > 0] = np.array(self.out_color).astype(np.uint8)

    def clear_all(self):
        EventHandler().image_mode = 0
        self.layerz = 0 * np.ones((self.Ly, self.Lx, 4), np.uint8)
        self.cell_pixel = np.zeros((self.NZ, self.Ly, self.Lx), np.uint32)
        self.out_pixel = np.zeros((self.NZ, self.Ly, self.Lx), np.uint32)
        self.cell_colors = np.array([255, 255, 255])[np.newaxis, :]
        EventHandler().number_of_cells = 0
        self.update_layer()

    def update_layer(self):
        if EventHandler().masks_on or EventHandler().outlines_on:
            self.layer.setImage(self.layerz, autoLevels=False)
        self.win.show()

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
            self.reset()
            EventHandler().dispatch_event(DisplayEvents.RESET_FOR_NEW_IMAGE)
            print('GUI_INFO: filename info:', self.filename)
            self.initialize_images(image)
            self.clear_all()
            self.loaded = True

    def reset(self):
        self.one_channel = False
        self.loaded = False
        self.strokes = []
        EventHandler().rois = 0
        self.cell_colors = np.array([255, 255, 255])[np.newaxis, :]
        # -- set menus to default -- #
        EventHandler().current_view = 0
        self.opacity = 128  # how opaque masks should be
        self.out_color = [200, 200, 255, 200]
        self.NZ, self.Ly, self.Lx = 1, 512, 512
        self.saturation = [[0, 255] for _ in range(self.NZ)]
        self.currentZ = 0
        self.layerz = 0*np.ones((self.Ly, self.Lx, 4), np.uint8)
        self.cell_pixel = np.zeros((1, self.Ly, self.Lx), np.uint32)
        self.out_pixel = np.zeros((1, self.Ly, self.Lx), np.uint32)
        self.update_plot()
        self.filename = []
        self.recompute_masks = False

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

    def select_cell(self, idx):
        self.prev_selected = self.selected
        self.selected = idx
        if self.selected > 0:
            z = self.currentZ
            self.layerz[self.cell_pixel[z] == idx] = np.array([255, 255, 255, self.opacity])
            self.update_layer()

    def unselect_cell(self):
        if self.selected > 0:
            idx = self.selected
            if idx < EventHandler().rois + 1:
                z = self.currentZ
                self.layerz[self.cell_pixel[z] == idx] = np.append(self.cell_colors[idx], self.opacity)
                if EventHandler().outlines_on:
                    self.layerz[self.out_pixel[z] == idx] = np.array(self.out_color).astype(np.uint8)
                self.update_layer()
        self.selected = 0

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            if self.selected > 0:
                self.remove_single_cell(self.selected)
                EventHandler().rois -= 1
                self.update_layer()
                EventHandler().dispatch_event(DisplayEvents.REMOVED_ROI)

    def remove_single_cell(self, idx):
        # remove from manual array
        self.selected = 0
        if self.NZ > 1:
            zextent = ((self.cell_pixel == idx).sum(axis=(1, 2)) > 0).nonzero()[0]
        else:
            zextent = [0]
        for z in zextent:
            cp = self.cell_pixel[z] == idx
            op = self.out_pixel[z] == idx
            # remove from self.cell_pixel and self.out_pixel
            self.cell_pixel[z, cp] = 0
            self.out_pixel[z, op] = 0
            if z == self.currentZ:
                # remove from mask layer
                self.layerz[cp] = np.array([0, 0, 0, 0])

            # reduce other pixels by -1
            self.cell_pixel[self.cell_pixel > idx] -= 1
            self.out_pixel[self.out_pixel > idx] -= 1

            # remove cell from lists
            # self.cell_colors = np.delete(self.cell_colors, [idx], axis=0)
            print('GUI_INFO: removed cell %d' % (idx - 1))

    def remove_masks_that_do_not_fall_in_range(self):
        roi_numbers, _ = np.unique(np.int32(self.cell_pixel), return_counts=True)
        roi_numbers = roi_numbers[1:]
        z = 0

        counter = 0
        number_of_removed_rois = 0
        for _ in range(len(roi_numbers)):
            counter += 1
            count_for_number = np.sum(self.cell_pixel == counter)
            count_for_number = (count_for_number**0.5) / ((np.pi**0.5)/2)

            if count_for_number < EventHandler().minimum_cell_diameter or count_for_number > EventHandler().maximum_cell_diameter:
                cp = self.cell_pixel[z] == counter
                op = self.out_pixel[z] == counter
                self.cell_pixel[z, cp] = 0
                self.out_pixel[z, op] = 0

                self.cell_pixel[self.cell_pixel > counter] -= 1
                self.out_pixel[self.out_pixel > counter] -= 1
                counter -= 1

                number_of_removed_rois += 1
        EventHandler().rois -= number_of_removed_rois

    # MAIN MENU METHODS FOR DEALING WITH EVENTS
    def handle_segmentation_menu_load_image(self):
        # Open File Dialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", ".jpg, .png, .tiff, .tif")

        # Output file_name
        if file_name:
            self.load_image(file_name)
    def handle_segmentation_menu_save_masks_tiff(self):
        print(SegmentationMenuEvents.SAVE_MASKS_FOR_MULTILAYER_TIFF)

    def handle_segmentation_menu_save_outlines_tiff(self):
        print(SegmentationMenuEvents.SAVE_OUTLINES_FOR_MULTILAYER_TIFF)

    def handle_segmentation_menu_save_masks_and_outlines_tiff(self):
        # Create a list of image data for each layer
        if self.loaded and self.cell_pixel.any() and self.out_pixel.any():
            # Writing the Masks Part of the Layer Z
            colormap = ((np.random.rand(1000000, 3) * 0.8 + 0.1) * 255).astype(np.uint8)
            rois_found = EventHandler().rois
            opacity = 30
            colors = colormap[:rois_found, :3]
            cell_colors = np.concatenate((np.array([[255, 255, 255]]), colors), axis=0).astype(np.uint8)
            layer_z = np.zeros((self.Ly, self.Lx, 4), np.uint8)
            layer_z[..., :3] = cell_colors[self.cell_pixel[self.currentZ], :]
            layer_z[..., 3] = opacity * (self.cell_pixel[self.currentZ] > 0).astype(np.uint8)

            # Writing the Outlines Part of Layer Z
            self.layerz[self.out_pixel[self.currentZ] > 0] = np.array(self.out_color).astype(np.uint8)

            # Specify the file name for the multi-layered TIFF file
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Masks and Outlines", "masks_outlines.tiff", "")
            img = cv2.imread(self.filename)
            images = [img, layer_z]
            # Save the multi-layered TIFF file
            imageio.mimwrite(file_name, images, format='TIFF', bigtiff=False)

    def handle_segmentation_menu_masks_only_npy(self):
        if self.loaded:
            if self.cell_pixel.any():
                file_name, _ = QFileDialog.getSaveFileName(self, "Save Masks .npy", "masks.npy", "")
                np.save(file_name, self.cell_pixel)

    def handle_segmentation_menu_outlines_only_npy(self):
        if self.loaded:
            if self.out_pixel.any():
                file_name, _ = QFileDialog.getSaveFileName(self, "Save Outlines .npy", "outlines.npy", "")
                np.save(file_name, self.out_pixel)
