from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
import cv2


class ImageProcessor(QWidget):
    # Signal emitted when an image modification occurs
    image_updated = pyqtSignal()

    def __init__(self, zoomable_label):
        super().__init__()
        self.zoomable_label = zoomable_label
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        draw_button = QPushButton('Draw', self)
        draw_button.clicked.connect(self.on_draw)

        layout.addWidget(draw_button)
        self.setLayout(layout)

    def on_draw(self):
        print('drawing')