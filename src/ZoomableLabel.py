from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
import numpy as np
from src.utils import Box
from src.config import config

class ZoomableLabel(QLabel):

    draw_signal = pyqtSignal(int, int) # Signal with x, y coordinates for the ImageProcessor

    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_image = None
        self.transformed_image = None # the original image after any image processing transformations
        self.subimage = None # part of self.transformed_image (to avoid drawing more than neccessary)
        self.img_width, self.img_height = None, None # width and height of original image
        self.subimage_selection = None # Box(left, top, width, height)
        self.scale_factor = 1.0 # cv2_image_coordinate * scale_factor -> widget_coordinate
        self.offset = QPoint(0, 0) # offset in widget coordinates
        self.last_mouse_pos = None
        self.mouse_pressed = None

        self.drawing_enabled = False # Flag to track if drawing mode is active (i.e. send events to ImageProcessor)

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
        self.transformed_image = self.original_image
        self.subimage = self.transformed_image
        self.subimage_selection = Box(0, 0, self.img_width, self.img_height)
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
        new_scale = self.scale_factor * factor
        if factor > 1:
            # Approximate the number of visible pixels. If its too small do not allow zoom in
            width = self.width() / new_scale
            height = self.height() / new_scale
            if min(width, height) < config['zoomableLabel']['min_pixels_per_side']:
                return
        elif new_scale < config['zoomableLabel']['minimum_scale']:
            # If the scale is too small do not allow zoomout
            return
        self.scale_factor = new_scale

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
            self.mouse_pressed = True

    def mouseMoveEvent(self, event):
        '''
        Handle dragging the image
        '''
        if not self.mouse_pressed:
            return

        if self.drawing_enabled:
            # Convert widget coordinates to image coordinates
            x = int((event.pos().x() - self.offset.x()) / self.scale_factor)
            y = int((event.pos().y() - self.offset.y()) / self.scale_factor)
            # Check if the coordinates are within the image bounds
            if 0 <= x < self.img_width and 0 <= y < self.img_height:
                self.draw_signal.emit(x, y)
        else:
            # Move the image
            delta = event.pos() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None
            self.mouse_pressed = False

    def paintEvent(self, event):
        ''' Draw the scaled and translated image '''
        if self.original_image is None:
            return # No image to display

        # Update the subimage
        self.update_subimage()

        # Convert OpenCV image to QImage
        height, width, channel = self.subimage.shape
        bytes_per_line = channel * width
        q_image = QImage(self.subimage.data.tobytes(), width, height, bytes_per_line, QImage.Format_RGB888)

        # Draw the scaled and translated image
        painter = QPainter(self)
        scaled_image = q_image.scaled(width * self.scale_factor, height * self.scale_factor, Qt.IgnoreAspectRatio, Qt.FastTransformation)
        painter.drawImage(self.offset, scaled_image)

    def update_subimage(self):
        '''
        Update self.subimage.
        Update the subimage only when we are close to the edge to make sure it contains the part of the image that we want to show
        '''
        old_subimage_selection = self.subimage_selection

        # Convert the offset to a position on the image
        offset_pos_subimage_x = -self.offset.x() / self.scale_factor
        offset_pos_subimage_y = -self.offset.y() / self.scale_factor
        offset_pos_image_x = self.subimage_selection.left + offset_pos_subimage_x
        offset_pos_image_y = self.subimage_selection.top + offset_pos_subimage_y

        # Estimate the width and height of the visible part of the image
        width = max(2, int(self.width() / self.scale_factor))
        height = max(2, int(self.height() / self.scale_factor))

        # Get a big subimage containing the visible part of the image
        left = max(0, int(offset_pos_image_x - width))
        top = max(0, int(offset_pos_image_y - height))
        right = min(self.img_width, int(offset_pos_image_x + 2 * width))
        bottom = min(self.img_height, int(offset_pos_image_y + 2 * height))

        # Update the subimage
        self.subimage = self.transformed_image[top:bottom, left:right]
        self.subimage_selection = Box(left, top, right - left, bottom - top)

        # Update the offset
        self.offset.setX(self.offset.x() + self.scale_factor * (self.subimage_selection.left - old_subimage_selection.left))
        self.offset.setY(self.offset.y() + self.scale_factor * (self.subimage_selection.top - old_subimage_selection.top))

    def update_transformed_image(self, transformed_image):
        '''
        Update self.transformed_image
        '''
        self.transformed_image = transformed_image
        self.subimage = self.transformed_image[self.subimage_selection.top : self.subimage_selection.top + self.subimage_selection.height,
                                               self.subimage_selection.left : self.subimage_selection.left + self.subimage_selection.width]
        self.update()