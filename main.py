import sys
import argparse
from PyQt5.QtWidgets import QMainWindow
from protein_screen import SliderForProteinFrame
from Custom_Widgets.Widgets import *
from segmentation_screen import EventHandler
from protein_screen import GlobalObject
from main_screen import MainMenu
from ui_interface import *

shadow_elements = {
    "frame_3",
    "frame_5",
    "frame_8"
}

list_of_colors = ["blue", "red", "green", "orange", "yellow", "purple", "white", "pink", "brown"]


# MAIN WINDOW CLASS
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set up the main menu for the screen being viewed
        MainMenu.create_main_menu(self)

        # Initially selected screen
        self.ui.percentage_bar_btn.setStyleSheet("""
        QPushButton {
            padding: 10px;
            border-radius: 5px;
            background-color: rgba(33,43,51,100);
            border: 1px solid black;
        }
        """)
        self.ui.tsne_button.setStyleSheet("""
        QPushButton {
            padding: 10px;
            border-radius: 5px;
            background-color: rgba(33,43,51,100);
            border: 1px solid black;
        }
        """)

        # Set Window Minimum Size
        self.setMinimumSize(850, 600)
        self.button_navigation()
        self.graph_button_navigation()

        for x in shadow_elements:
            # Shadow effect style
            effect = QtWidgets.QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(18)
            effect.setYOffset(0)
            effect.setXOffset(0)
            effect.setColor(QColor(0, 0, 0, 255))
            getattr(self.ui, x).setGraphicsEffect(effect)

        GlobalObject().add_event_listener("NEW_DATA", self.update_interface_based_on_data)
        self.ui.plot_button.clicked.connect(lambda: self.update_tsne_graph_event())

        # SHOW WINDOW
        self.show()

    def update_tsne_graph_event(self):
        GlobalObject().num_components = self.ui.numberOfComponentsSpinBox.value()
        if self.ui.verboseCheckBox.isChecked():
            GlobalObject().verbose = 1
        else:
            GlobalObject().verbose = 0
        GlobalObject().perplexity = self.ui.perplexitySpinBox.value()
        GlobalObject().num_iterations = self.ui.numberOfIterationsSpinBox.value()
        GlobalObject().dispatch_event("PLOT_TSNE")

    def update_interface_based_on_data(self):
        data_frame = GlobalObject().data_frame

        # Delete All Children Before Adding More
        for i in reversed(range(self.ui.verticalLayout_19.count())):
            self.ui.verticalLayout_19.itemAt(i).widget().setParent(None)

        counter = 0
        for column in data_frame.columns:
            if column == "Areax":
                continue
            elif column == "AreaY":
                continue
            elif column == "LocalX":
                continue
            elif column == "LocalY":
                continue
            elif column == "GlobX":
                continue
            elif column == "GlobY":
                continue
            new_frame_for_slider = SliderForProteinFrame(self.ui.scrollAreaWidgetContents_3, data_frame.columns,
                                                         list_of_colors[counter], current_list_index=counter)
            self.ui.verticalLayout_19.addWidget(new_frame_for_slider)
            counter += 1

    def button_navigation(self):
        self.ui.percentage_bar_btn.clicked.connect(lambda: self.display(0))
        self.ui.temperature_bar_btn.clicked.connect(lambda: self.display(1))
        self.ui.nested_donut_btn.clicked.connect(lambda: self.display(2))
        self.ui.line_chart_btn.clicked.connect(lambda: self.display(3))
        self.ui.bar_charts_btn.clicked.connect(lambda: self.display(4))

    def graph_button_navigation(self):
        self.ui.tsne_button.clicked.connect(lambda: self.display_graph_algorithm(0))
        self.ui.umap_button.clicked.connect(lambda: self.display_graph_algorithm(1))

    def display_graph_algorithm(self, i):
        if i == 0:
            print("Displaying tsne")
            self.ui.tsne_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: rgba(33,43,51,100);
                border: 1px solid black;
            }
            """)
            self.ui.umap_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: rgb(222, 222, 222);
                border: 1px solid black;
            }
            QPushButton:hover {
                background-color: rgba(33,43,51,100);
                cursor: pointer;
            }
            """)
            self.ui.graph_stacked_widget.setCurrentIndex(i)
        else:
            print("Displaying UMAP")
            self.ui.umap_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: rgba(33,43,51,100);
                border: 1px solid black;
            }
            """)
            self.ui.tsne_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: rgb(222, 222, 222);
                border: 1px solid black;
            }
            QPushButton:hover {
                background-color: rgba(33,43,51,100);
                cursor: pointer;
            }
            """)
            self.ui.graph_stacked_widget.setCurrentIndex(i)

    def display(self, i):
        self.reset_background_for_all_left_menu_buttons()
        self.set_dark_background_for_selected_button(i)
        self.ui.stackedWidget.setCurrentIndex(i)

    def set_dark_background_for_selected_button(self, i):
        if i == 0:
            self.ui.percentage_bar_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: rgba(33,43,51,100);
                border: 1px solid black;
            }
            """)
        elif i == 1:
            self.ui.temperature_bar_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: rgba(33,43,51,100);
                border: 1px solid black;
            }
            QPushButton:hover {
                background-color: rgba(33,43,51,100);
                cursor: pointer;
            }
            """)
        elif i == 2:
            self.ui.nested_donut_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: rgba(33,43,51,100);
                border: 1px solid black;
            }
            QPushButton:hover {
                background-color: rgba(33,43,51,100);
                cursor: pointer;
            }
            """)
        elif i == 3:
            self.ui.line_chart_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: rgba(33,43,51,100);
                border: 1px solid black;
            }
            QPushButton:hover {
                background-color: rgba(33,43,51,100);
                cursor: pointer;
            }
            """)
        else:
            self.ui.bar_charts_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                background-color: rgba(33,43,51,100);
                border: 1px solid black;
            }
            QPushButton:hover {
                background-color: rgba(33,43,51,100);
                cursor: pointer;
            }
            """)

    def reset_background_for_all_left_menu_buttons(self):
        self.ui.percentage_bar_btn.setStyleSheet("""
        QPushButton {
            padding: 10px;
            border-radius: 5px;
            background-color: rgb(222, 222, 222);
            border: 1px solid black;
        }
        QPushButton:hover {
            background-color: rgba(33,43,51,100);
            cursor: pointer;
        }
        """)
        self.ui.temperature_bar_btn.setStyleSheet("""
        QPushButton {
            padding: 10px;
            border-radius: 5px;
            background-color: rgb(222, 222, 222);
            border: 1px solid black;
        }
        QPushButton:hover {
            background-color: rgba(33,43,51,100);
            cursor: pointer;
        }
        """)
        self.ui.nested_donut_btn.setStyleSheet("""
        QPushButton {
            padding: 10px;
            border-radius: 5px;
            background-color: rgb(222, 222, 222);
            border: 1px solid black;
        }
        QPushButton:hover {
            background-color: rgba(33,43,51,100);
            cursor: pointer;
        }
        """)
        self.ui.line_chart_btn.setStyleSheet("""
        QPushButton {
            padding: 10px;
            border-radius: 5px;
            background-color: rgb(222, 222, 222);
            border: 1px solid black;
        }
        QPushButton:hover {
            background-color: rgba(33,43,51,100);
            cursor: pointer;
        }
        """)
        self.ui.bar_charts_btn.setStyleSheet("""
        QPushButton {
            padding: 10px;
            border-radius: 5px;
            background-color: rgb(222, 222, 222);
            border: 1px solid black;
        }
        QPushButton:hover {
            background-color: rgba(33,43,51,100);
            cursor: pointer;
        }
        """)


# EXECUTE APP
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--gpu', default=False,
                        help='gpu available')
    args = parser.parse_args()

    if args.gpu:
        EventHandler().gpu = args.gpu   

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
