from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
import cv2
import numpy as np
from src.ZoomableLabel import ZoomableLabel


class ImageProcessor(QWidget):

    def __init__(self, zoomable_label):
        super().__init__()
        self.zoomable_label = zoomable_label
        self.zoomable_label:ZoomableLabel
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        draw_button = QPushButton('Draw', self)
        draw_button.setCheckable(True)
        draw_button.clicked.connect(self.on_draw)

        layout.addWidget(draw_button)
        self.setLayout(layout)

    def on_draw(self):
        self.drawing_enabled = True
        self.zoomable_label.drawing_enabled = self.drawing_enabled

    def transform(self, image):
        # Apply transformations to the image
        transformed_image = image
        # Emit the signal with the transformed image when done
        self.image_transformed.emit(transformed_image)

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
            transformed_image = cv2.circle(self.zoomable_label.transformed_image.copy(), (x, y), thickness, color, -1)
            # Update the ZoomableLabel with the modified image
            self.zoomable_label.update_transformed_image(transformed_image)