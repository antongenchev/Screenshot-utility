from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtCore import Qt, QPoint
import numpy as np

class ZoomableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_image = None
        self.subimage = None # part of self.original_image (to avoid drawing more than neccessary)
        self.img_width, self.img_height = None, None
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.last_mouse_pos = None

    def setImage(self, image):
        '''
        Set the OpenCV image and convert it to QImage
        '''
        self.original_image = image
        # Calculate new initial scale factor
        self.img_height, self.img_width, _ = self.original_image.shape
        scale_horizontal = self.width() / self.img_width
        scale_vertical = self.height() / self.img_height
        self.scale_factor = min(scale_horizontal, scale_vertical) # scale to fit perfectly

        # Calculate new offset so that the image is centered
        if scale_vertical > scale_horizontal:
            # Center vertically
            scaled_height = self.img_height * self.scale_factor # the height of the displayed image
            vertical_offset = (self.height() - scaled_height) / 2 # center vertically
            self.offset = QPoint(0, int(vertical_offset))
        else:
            # Center horizontally
            scaled_width = self.img_width * self.scale_factor # the width of the displayed image
            horizontal_offset = (self.width() - scaled_width) / 2 # center hotizontally
            self.offset = QPoint(int(horizontal_offset), 0)

        self.update() # Update the label to repaint with the new image

    def wheelEvent(self, event):
        '''
        Scale the image on scrolling the mouse: zoom in - zoom out,
        with the zoom cetnered around the mouse cursor.
        '''
        mouse_pos_widget = event.pos()
        # Convert the mouse position to image coordinates
        mouse_pos_image_x = (mouse_pos_widget.x() - self.offset.x()) / self.scale_factor
        mouse_pos_image_y = (mouse_pos_widget.y() - self.offset.y()) / self.scale_factor
        # Determine and apply zoom factor
        factor = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.scale_factor *= factor
        # Update the offset to ensure the mouse position stays at the same point in the image
        new_mouse_pos_image_x = (mouse_pos_widget.x() - self.offset.x()) / self.scale_factor
        new_mouse_pos_image_y = (mouse_pos_widget.y() - self.offset.y()) / self.scale_factor
        self.offset.setX(self.offset.x() + int((new_mouse_pos_image_x - mouse_pos_image_x) * self.scale_factor))
        self.offset.setY(self.offset.y() + int((new_mouse_pos_image_y - mouse_pos_image_y) * self.scale_factor))
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

        # Update the subimage
        self.update_sub_image()

        # Convert OpenCV image to QImage
        height, width, channel = self.subimage.shape
        bytes_per_line = channel * width
        q_image = QImage(self.subimage.data.tobytes(), width, height, bytes_per_line, QImage.Format_RGB888)

        # Draw the scaled and translated image
        painter = QPainter(self)
        scaled_image = q_image.scaled(width * self.scale_factor, height * self.scale_factor, Qt.IgnoreAspectRatio, Qt.FastTransformation)
        print(f'{self.offset=}')
        painter.drawImage(self.offset, scaled_image)

    def update_sub_image(self):
        '''
        Update self.subimage.
        Update the subimage only when we are close to the edge to make sure it contains the part of the image that we want to show
        '''
        # Estimate the portion of the opencv image that will fit inside the widget
        left = int(self.offset.x() / self.scale_factor) # approximate the column idx of the opencv image
        top = int(self.offset.y() / self.scale_factor) # approximate the row idx of the opencv image
        width = int(self.width() /self.scale_factor) # approxiimate the width
        height = int(self.height() /self.scale_factor) # approxiimate the height
        # Expand the portion to cut more than what is required
        left = max(0, left - 2 * width)
        top = max(0, top - 2 * height)
        right = min(self.img_width, left + 4 * width)
        bottom = min(self.img_height, height + 4 * height)
        self.subimage = self.original_image[top:bottom, left:right]
