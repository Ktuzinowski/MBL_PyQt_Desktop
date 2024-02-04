from Custom_Widgets import QMainWindow
from PyQt5.QtWidgets import QAction

from main_screen import SegmentationMenuEvents, ProteinMenuEvents
from segmentation_screen import EventHandler
from protein_screen import GlobalObject


def create_main_menu(parent: QMainWindow):
    main_menu = parent.menuBar()
    protein_menu = main_menu.addMenu("&Protein")
    segmentation_menu = main_menu.addMenu("&Segmentation")

    main_menu.setStyleSheet('color: black; font-family: times; font-size: 12px; font-size: 12px;')

    # Load Image Data Protein
    load_image_protein = QAction("&Load image (*.tif, *.png, *.jpg)", parent)
    load_image_protein.setShortcut("Ctrl+L")
    load_image_protein.triggered.connect(
        lambda: GlobalObject().dispatch_event(ProteinMenuEvents.LOAD_IMAGE_PROTEIN))
    protein_menu.addAction(load_image_protein)

    # Load Image Data
    load_image_action = QAction("&Load image (*.tif, *.png, *.jpg)", parent)
    load_image_action.setShortcut("Ctrl+L")
    load_image_action.triggered.connect(
        lambda: EventHandler().dispatch_event(SegmentationMenuEvents.LOAD_IMAGE))
    segmentation_menu.addAction(load_image_action)

    # Save Masks for Multi-Layer TIFF
    save_masks_action = QAction("&Save Masks for Multi-Layer TIFF", parent)
    save_masks_action.setShortcut("Ctrl+M")
    save_masks_action.triggered.connect(
        lambda: EventHandler().dispatch_event(SegmentationMenuEvents.SAVE_MASKS_FOR_MULTILAYER_TIFF))
    segmentation_menu.addAction(save_masks_action)

    # Save Outlines for Multi-Layer TIFF
    save_outlines_action = QAction("&Save Outlines for Multi-Layer TIFF", parent)
    save_outlines_action.setShortcut("Ctrl+O")
    save_outlines_action.triggered.connect(
        lambda: EventHandler().dispatch_event(SegmentationMenuEvents.SAVE_OUTLINES_FOR_MULTILAYER_TIFF))
    segmentation_menu.addAction(save_outlines_action)

    # Save Masks and Outlines for Multi-Layer TIFF
    save_masks_and_outlines_action = QAction("&Save Masks and Outlines for Multi-Layer TIFF", parent)
    save_masks_and_outlines_action.triggered.connect(
        lambda: EventHandler().dispatch_event(SegmentationMenuEvents.SAVE_MASKS_AND_OUTLINES_FOR_MULTILAYER_TIFF))
    segmentation_menu.addAction(save_masks_and_outlines_action)

    # Save Masks on their Own
    save_masks_only_action = QAction("&Save Masks Only (*.npy)", parent)
    save_masks_only_action.triggered.connect(
        lambda: EventHandler().dispatch_event(SegmentationMenuEvents.SAVE_MASKS_ONLY_NPY))
    segmentation_menu.addAction(save_masks_only_action)

    # Save Outlines on their Own
    save_outlines_only_action = QAction("&Save Outlines Only (*.npy)", parent)
    save_outlines_only_action.triggered.connect(
        lambda: EventHandler().dispatch_event(SegmentationMenuEvents.SAVE_OUTLINES_ONLY_NPY))
    segmentation_menu.addAction(save_outlines_only_action)
