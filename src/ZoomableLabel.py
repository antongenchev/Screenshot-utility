from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtCore import Qt, QPoint
import numpy as np

class ZoomableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_image = None
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.last_mouse_pos = None

    def setImage(self, image):
        '''
        Set the OpenCV image and convert it to QImage
        '''
        self.original_image = image
        self.update()  # Update the label to repaint with the new image

    def wheelEvent(self, event):
        '''
        Scale the image on scrolling the mouse: zoom in - zoom out
        '''
        factor = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.scale_factor *= factor
        self.update()

    def mousePressEvent(self, event):
        '''
        Start dragging the image
        '''
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        '''
        Handle dragging the image
        '''
        if self.last_mouse_pos is not None:
            delta = event.pos() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None

    def paintEvent(self, event):
        ''' Draw the scaled and translated image '''
        if self.original_image is None:
            return # No image to display
        # Convert OpenCV image to QImage
        height, width, channel = self.original_image.shape
        bytes_per_line = channel * width
        q_image = QImage(self.original_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        # Draw the scaled and translated image
        painter = QPainter(self)
        scaled_image = q_image.scaled(width * self.scale_factor, height * self.scale_factor, Qt.IgnoreAspectRatio, Qt.FastTransformation)
        painter.drawImage(self.offset, scaled_image)

