import functools

from PyQt5.QtWidgets import QLabel, QSlider, QCheckBox, QComboBox, QSizePolicy, QVBoxLayout, QFrame, QHBoxLayout, QColorDialog
from PyQt5.QtCore import Qt, QSize, QCoreApplication


class SliderForProteinFrame(QFrame):
    def __init__(self, parent=None, column_names=None, color_for_display=None, current_list_index=0):
        super(SliderForProteinFrame, self).__init__(parent)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
        self.setMaximumSize(QSize(300, 80))
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("frame_32")

        self.verticalLayout_17 = QVBoxLayout(self)
        self.verticalLayout_17.setContentsMargins(0, 8, 8, -1)
        self.verticalLayout_17.setObjectName("verticalLayout_18")

        # Check Box and Combo Box Frame
        self.frame_11 = QFrame(self)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(size_policy)
        self.frame_11.setMaximumSize(QSize(300, 50))
        self.frame_11.setFrameShape(QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Raised)
        self.frame_11.setObjectName("frame_12")

        # Horizontal for Combo Box and Check Box
        self.horizontalLayout_4 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_6")
        # Create Combo Box
        self.comboBox_14 = QComboBox(self.frame_11)
        self.comboBox_14.setStyleSheet("QComboBox { padding: 4px; }")
        self.comboBox_14.setObjectName("comboBox_17")
        for _ in column_names:
            self.comboBox_14.addItem("")
        self.horizontalLayout_4.addWidget(self.comboBox_14)
        # Create Check Box
        self.checkBox_7 = QCheckBox(self.frame_11)
        self.checkBox_7.setObjectName("checkBox_8")

        self.horizontalLayout_4.addWidget(self.checkBox_7)
        self.verticalLayout_17.addWidget(self.frame_11)

        # Create Frame for Slider and Color Block
        self.frame_10 = QFrame(self)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.frame_10.sizePolicy().hasHeightForWidth())
        self.frame_10.setSizePolicy(size_policy)
        self.frame_10.setMaximumSize(QSize(300, 50))
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.frame_10.setObjectName("frame_11")
        self.horizontalLayout_3 = QHBoxLayout(self.frame_10)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_4")
        self.horizontalSlider_7 = QSlider(self.frame_10)
        self.horizontalSlider_7.setOrientation(Qt.Horizontal)
        self.horizontalSlider_7.setObjectName("horizontalSlider_8")
        self.horizontalLayout_3.addWidget(self.horizontalSlider_7)
        self.label_5 = QLabel(self.frame_10)
        size_of_label_5 = 26
        self.label_5.setMinimumSize(QSize(size_of_label_5, size_of_label_5))
        self.label_5.setMaximumSize(QSize(size_of_label_5, size_of_label_5))
        self.label_5.setAutoFillBackground(False)
        self.label_5.setStyleSheet(
            "background-color: " + color_for_display + "; "
            + "border-radius: " + "13px" + "; "
        )
        self.label_5.mousePressEvent = functools.partial(self.color_block_clicked, source_object=self.label_5)
        self.label_5.setText("")
        self.label_5.setObjectName("label_6")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.verticalLayout_17.addWidget(self.frame_10)
        _translate = QCoreApplication.translate

        counter = 0
        for column in column_names:
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
            self.comboBox_14.setItemText(counter, _translate("MainWindow", column))
            counter += 1
        self.comboBox_14.setCurrentIndex(current_list_index)

    def color_block_clicked(self, event, source_object=None):
        color = QColorDialog.getColor()
        if color.isValid():
            self.label_5.setStyleSheet(
                "background-color: {}".format(color.name()) + "; " + "border-radius: " + "13px" + ";")
