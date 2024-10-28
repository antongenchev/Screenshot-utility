from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
import cv2
import numpy as np
from src.ZoomableLabel import ZoomableLabel
from enum import IntEnum, auto
from scipy.interpolate import CubicSpline


class ImageProcessor(QWidget):

    # The available image processing tools
    class tools(IntEnum):
        move = 0
        pencil = auto()

    def __init__(self, zoomable_label):
        super().__init__()
        self.zoomable_label = zoomable_label
        self.zoomable_label:ZoomableLabel
        self.current_tool = self.tools.move
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        pencil_button = QPushButton('Draw', self)
        pencil_button.setCheckable(True)
        pencil_button.clicked.connect(self.on_pencil)

        layout.addWidget(pencil_button)
        self.setLayout(layout)

    def on_pencil(self):
        self.drawing_enabled = True
        self.zoomable_label.drawing_enabled = self.drawing_enabled

    def handle_draw(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel.

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        if self.drawing_enabled:
            # Apply drawing on the image at the (x, y) location
            color = (255, 0, 0)  # Red color for example
            thickness = 5  # Example thickness
            cv2.circle(self.zoomable_label.transformed_image, (x, y), thickness, color, -1)
            # Update the ZoomableLabel with the modified image
            self.zoomable_label.update_transformed_image()

    def handle_start_draw(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel for left mouse button down event

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        pass

    def handle_stop_draw(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel for left mouse button release event

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        pass
