import sys
from PyQt5.QtWidgets import QMainWindow
from myWidgets import SliderForProteinFrame
from Custom_Widgets.Widgets import *
from globalobject import GlobalObject
from ui_interface import *

shadow_elements = {
    "frame_3",
    "frame_5",
    "frame_8"
}

list_of_colors = ["blue", "red", "green", "orange", "yellow", "purple", "white", "pink", "brown"]


# MAIN WINDOW CLASS
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        # Set Window Minimum Size
        self.setMinimumSize(850, 600)
        self.button_navigation()

        for x in shadow_elements:
            # Shadow effect style
            effect = QtWidgets.QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(18)
            effect.setYOffset(0)
            effect.setXOffset(0)
            effect.setColor(QColor(0, 0, 0, 255))
            getattr(self.ui, x).setGraphicsEffect(effect)

        GlobalObject().add_event_listener("NEW_DATA", self.update_interface_based_on_data)
        # SHOW WINDOW
        self.show()

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

    def display(self, i):
        self.ui.stackedWidget.setCurrentIndex(i)


# EXECUTE APP
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
