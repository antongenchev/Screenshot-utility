from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QWidget
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor
import os
import math
import numpy as np
from typing import Tuple
from enum import IntEnum, auto
from src.DrawableElement import DrawableElement
from src.utils import Box
from src.config import *

class zone_areas(IntEnum):
    center = 0 # used for moving
    left = auto()
    top = auto()
    right = auto()
    bottom = auto()
    top_left = auto()
    top_right = auto()
    bottom_left = auto()
    bottom_right = auto()
    circle = auto() # used for rotation
    outside = auto() # outside of anything clickable

class actions(IntEnum):
    none = 0 # do nothing
    rotate = auto() # rotating the box
    move = auto() # dragging the box
    resize = auto() # resize the box

class RotatableBox(QWidget):

    def __init__(self,
                 parent=None,
                 zoomable_widget = None,
                 image_processor = None,
                 drawable_element:DrawableElement = None):
        super().__init__(parent)
        self.zoomable_widget = zoomable_widget
        self.image_processor = image_processor
        self.drawable_element = drawable_element

        # Define the target for the events that do not hit the rotatable box
        self.target = self.zoomable_widget.overlay

        # Initialise the settings for drawing the box
        self.circle_radius = 4
        self.circle_top_offset = 5
        self.circle_clickable_radius = 4
        self.resize_clickable_border = 4

        # The 'shown_' attributes needed to draw the rectangle. Updated self.update_shown_coordinates()
        self.shown_left:float = None
        self.shown_top:float = None
        self.shown_right:float = None
        self.shown_bottom:float = None
        self.shown_width:float = None
        self.shown_height:float = None
        self.shown_reflected:bool = False # is there reflection in x. In y is in x with rotation by 180
        self.shown_angle:float = None

        self.current_action = actions.none

        self.last_clicked_zone:zone_areas = None

        # Members used for moving
        self.shown_drag_offset:QPoint = None # the difference between mouse and box's origin (left, top)
        # Members used for rotating
        self.initial_angle:float = None # used to calculate the angle difference
        self.final_angle:float = None # the final angle after rotating
        self.shown_center_x_original:float = None # the initial center at the start of rotating. x-cor
        self.shown_center_y_original:float = None # the initial center at the start of rotating. y-cor
        self.original_transformation = None # the original transformation before starting to rotate
        # Members used for resizing
        self.original_left = None # The original tx of the transformation
        self.original_top = None # The original ty of the transformation
        self.original_right = None # The original tx + width of the transformation
        self.original_bottom = None # The original tx + height of the transformation

        self.initGUI()

    def initGUI(self):
        '''
        Initialise the GUI
        '''
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setGeometry(self.zoomable_widget.zoomable_label.geometry())
        self.show()

    def paintEvent(self, event):
        # Update the coordinates of the box
        self.update_shown_coordinates()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Transparent background
        painter.setBrush(Qt.NoBrush)

        # Set a red border for the rectangle
        pen = QPen(QColor("red"), 3)
        painter.setPen(pen)

        # Rotate the painter around the center of the rectangle
        painter.translate(self.shown_left, self.shown_top)
        painter.rotate(self.shown_angle)
        painter.translate(-self.shown_left, -self.shown_top)

        # Draw the rectangle
        rect = QRect(QPoint(self.shown_left, self.shown_top), QPoint(self.shown_right, self.shown_bottom))
        painter.drawRect(rect)

        # Draw a circle above the rectangle
        circle_radius = 5
        center_x = (self.shown_left + self.shown_right) / 2
        center_y = self.shown_top - self.circle_radius - self.circle_top_offset
        painter.drawEllipse(center_x - circle_radius, center_y - circle_radius, circle_radius * 2, circle_radius * 2)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            mouse_position = event.pos()
            zone_clicked = self.get_zone(mouse_position)
            self.update_cursor(zone_clicked)
            if zone_clicked == zone_areas.center:
                # Drag the box
                self.current_action = actions.move
                self.shown_drag_offset = mouse_position - QPoint(self.shown_left, self.shown_top)
                return
            elif zone_clicked == zone_areas.circle:
                # Rotate the box
                self.current_action = actions.rotate
                self.shown_center_x_original, self.shown_center_y_original = self.get_shown_center()
                self.original_transformation = self.drawable_element.get_transformation()
                self.initial_angle = self.get_angle_from_center(mouse_position)
                return
            elif zone_clicked != zone_areas.outside:
                # Resize the box
                self.current_action = actions.resize
                self.last_clicked_zone = zone_clicked
                self.original_transformation = self.drawable_element.get_transformation()
                self.get_original_shown_borders()
                return
        self.target.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.current_action == actions.move:
            self.move_box(event.pos())
        elif self.current_action == actions.rotate:
            self.rotate_box(event.pos())
        elif self.current_action == actions.resize:
            self.resize_box(event.pos())
        else:
            self.update_cursor(self.get_zone(event.pos()))
            self.target.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.current_action = actions.none
        self.update_cursor(self.get_zone(event.pos()))
        self.target.mouseReleaseEvent(event)

    def wheelEvent(self, event):
        self.target.wheelEvent(event)

    def update_transformation(self):
        '''
        Update the transformation of the Drawable Element based on the offset, rotation, and scale
        of the RotatbleBox widget
        '''
        pass

    def move_box(self, mouse_position:QPoint) -> None:
        '''
        Handle the logic for moving the box
        '''
        # Get the ZoomableLabel info
        zoomable_label = self.zoomable_widget.zoomable_label
        selection = zoomable_label.subimage_selection
        offset = zoomable_label.offset
        scale_factor = zoomable_label.scale_factor

        # Calculate the new position of the center
        new_shown_center = mouse_position - self.shown_drag_offset

        # Convert the shown position into the real offset position (tx, ty)
        tx = (new_shown_center.x() - offset.x()) / scale_factor + selection.left
        ty = (new_shown_center.y() - offset.y()) / scale_factor + selection.top

        # Redraw the widget with the new offset
        self.drawable_element.transformation[:, 2] = [tx, ty]
        self.image_processor.apply_element_transformation(self.drawable_element)
        self.update()

    def rotate_box(self, mouse_position:QPoint) -> None:
        '''
        Handle the logic for rotating the box
        '''
        # Calculate the change in angle
        delta_angle = self.get_angle_from_center(mouse_position) - self.initial_angle

        # Extract transformation components
        transformation = self.drawable_element.transformation
        a, b = transformation[0, 0], transformation[0, 1]
        c, d = transformation[1, 0], transformation[1, 1]
        tx, ty = transformation[0, 2], transformation[1, 2]
        image_width = self.drawable_element.image.shape[1]
        image_height = self.drawable_element.image.shape[0]
        # Calculate the scale factors
        scale_x = math.sqrt(a**2 + b**2)
        scale_y = math.sqrt(c**2 + d**2)
        # Compute the true center of the rectangle after scaling
        center = self.original_transformation @ np.array([image_width / 2, image_height / 2, 1])
        center_x = center[0]
        center_y = center[1]

        # Translate to origin
        translation_to_origin = np.array([
            [1, 0, -center_x],
            [0, 1, -center_y],
            [0, 0, 1]
        ])
        # Apply rotation
        angle_radians = np.radians(delta_angle)
        cos_angle = np.cos(angle_radians)
        sin_angle = np.sin(angle_radians)
        rotation_matrix = np.array([
            [cos_angle, -sin_angle, 0],
            [sin_angle, cos_angle, 0],
            [0, 0, 1]
        ])
        # Translate back
        translation_back = np.array([
            [1, 0, center_x],
            [0, 1, center_y],
            [0, 0, 1]
        ])

        # Combine transformations
        original_transformation = np.vstack([self.original_transformation, [0, 0, 1]]) # convert affine -> 3x3
        final_transformation_matrix = (
            translation_back @ rotation_matrix @ translation_to_origin @ original_transformation
        )
        self.drawable_element.transformation = final_transformation_matrix[:2, :] # convert 3x3 -> affine
        # Redraw the widget with the new angle
        self.image_processor.apply_element_transformation(self.drawable_element)
        self.update()

    def resize_box(self, mouse_position:QPoint) -> None:
        '''
        Handle the logic for resizing the box
        '''
        # Get the ZoomableLabel info
        zoomable_label = self.zoomable_widget.zoomable_label
        selection = zoomable_label.subimage_selection
        offset = zoomable_label.offset
        scale_factor = zoomable_label.scale_factor

        # Compute the scale and rotation from the original transformation
        U, S, Vt = np.linalg.svd(self.original_transformation[:, :2])
        rotation_matrix = U @ Vt # Rotation matrix (orthonormal part)
        # Undo rotation by using the transpose of the rotation matrix (equivalent to its inverse)
        undo_rotation = rotation_matrix.T

        # Undo the rotation of the mouse coordinates. Unrotate around (shown_left, shown_top)
        mouse_pos_vec = np.array([mouse_position.x() - self.shown_original_left, mouse_position.y() - self.shown_original_top])
        rotated_mouse_vec = undo_rotation @ mouse_pos_vec
        mouse_position = QPoint(rotated_mouse_vec[0] + self.shown_original_left, rotated_mouse_vec[1] + self.shown_original_top)

        # Get the default tx, ty. Use if we do not rescale from the left or top respectively.
        tx, ty = self.original_transformation[:, 2]
        # The default rescaling
        x_scale, y_scale = 1, 1

        # Calculate the original width and height before rescaling
        original_signed_width = abs(self.shown_original_right - self.shown_original_left)
        original_height = self.shown_original_bottom - self.shown_original_top
        if min(abs(original_signed_width), original_height) < 1:
            raise Exception(f'Width and heights must be at least 1: {original_signed_width=} {original_height=}')

        # Avoid small width
        fixed_border_x_coordinate = None
        if self.last_clicked_zone in [zone_areas.left, zone_areas.top_left, zone_areas.bottom_left]:
            fixed_border_x_coordinate = self.shown_original_right
        elif self.last_clicked_zone in [zone_areas.right, zone_areas.top_right, zone_areas.bottom_right]:
            fixed_border_x_coordinate = self.shown_original_left
        if fixed_border_x_coordinate is not None:
            if -2 < mouse_position.x() - fixed_border_x_coordinate <= 0:
                new_x = fixed_border_x_coordinate - 2
            elif 0 < mouse_position.x() - fixed_border_x_coordinate < 2:
                new_x = fixed_border_x_coordinate + 2
            else:
                new_x = mouse_position.x()

        # Avoid small height
        fixed_border_y_coordinate = None
        if self.last_clicked_zone in [zone_areas.top, zone_areas.top_left, zone_areas.top_right]:
            fixed_border_y_coordinate = self.shown_original_bottom
        elif self.last_clicked_zone in [zone_areas.bottom, zone_areas.bottom_left, zone_areas.bottom_right]:
            fixed_border_y_coordinate = self.shown_original_top
        if fixed_border_y_coordinate is not None:
            if -2 < mouse_position.y() - fixed_border_y_coordinate <= 0:
                new_y = fixed_border_y_coordinate - 2
            elif 0 < mouse_position.y() - fixed_border_y_coordinate < 2:
                new_y = fixed_border_y_coordinate + 2
            else:
                new_y = mouse_position.y()

        # Calculate the horizontal rescaling
        if self.last_clicked_zone in [zone_areas.left, zone_areas.top_left, zone_areas.bottom_left]:
            # Handle rescaling from the left border
            new_signed_width = fixed_border_x_coordinate - new_x
            x_scale = new_signed_width / original_signed_width
        elif self.last_clicked_zone in [zone_areas.right, zone_areas.top_right, zone_areas.bottom_right]:
            # Handle rescaling from the right border
            new_signed_width = new_x - fixed_border_x_coordinate
            x_scale = new_signed_width / original_signed_width

        # Calculate the vertical rescaling
        if self.last_clicked_zone in [zone_areas.top, zone_areas.top_left, zone_areas.top_right]:
            # Handle rescaling from the top border
            new_signed_height = fixed_border_y_coordinate - new_y
            y_scale = new_signed_height / original_height
        elif self.last_clicked_zone in [zone_areas.bottom, zone_areas.bottom_left, zone_areas.bottom_right]:
            # Handle rescaling from the bottom border
            new_height = new_y - fixed_border_y_coordinate
            y_scale = new_height / original_height

        # Calculate the offset (tx, ty)
        if self.last_clicked_zone in [zone_areas.left, zone_areas.bottom_left]:
            delta_x = (new_x - self.shown_original_left) / scale_factor
            tx = tx + delta_x * math.cos(math.radians(self.shown_angle))
            ty = ty + delta_x * math.sin(math.radians(self.shown_angle))
        elif self.last_clicked_zone in [zone_areas.top, zone_areas.top_right]:
            delta_y = (new_y - self.shown_original_top) / scale_factor
            print(delta_y)
            tx = tx - delta_y * math.sin(math.radians(self.shown_angle))
            ty = ty + delta_y * math.cos(math.radians(self.shown_angle))

        # Create the scaling matrix
        scaling_matrix = np.array([
            [x_scale, 0],
            [0, y_scale]
        ])

        # Apply scaling, then reapply the original rotation
        new_transform = rotation_matrix @ scaling_matrix @ undo_rotation @ self.original_transformation[:, :2]

        # Combine with the translation part from the original affine matrix
        new_affine = np.zeros((2, 3))
        new_affine[:, :2] = new_transform
        new_affine[:, 2] = [tx, ty] # Keep the original translation offsets

        self.drawable_element.transformation = new_affine
        # Redraw the wdiget with the new scaling
        self.image_processor.apply_element_transformation(self.drawable_element)
        self.update()

    def update_shown_coordinates(self):
        '''
        When the ZoomableLabel is used to move or scale the displayed image the overlay needs to be
        rerendered. This function recalculates the rotation angle and the rectangle dimensions based
        on the DrawableElement transformation and the ZoomableLabel scale and offset.
        '''
        # Get the DrawableElement info
        transformation = self.drawable_element.transformation
        a, b, tx = transformation[0, :]
        c, d, ty = transformation[1, :]
        abs_scale_x = math.sqrt(a**2 + c**2) # correct up to +/- sign
        scale_y = math.sqrt(b**2 + d**2)
        shape = self.drawable_element.image.shape

        # Get the ZoomableLabel info
        zoomable_label = self.zoomable_widget.zoomable_label
        selection = zoomable_label.subimage_selection
        offset = zoomable_label.offset
        scale_factor = zoomable_label.scale_factor

        # Calculate the new shown position, size and rotation for rendering the box
        self.shown_width = scale_factor * abs_scale_x * shape[1]
        self.shown_height = scale_factor * scale_y * shape[0]

        # Get the correct left, top
        self.shown_left = (tx - selection.left) * scale_factor + offset.x()
        self.shown_top = (ty - selection.top) * scale_factor + offset.y()

        # Determine if there are reflections (true iff determinant < 0)
        det = a*d - b*c
        self.shown_reflected = det < 0

        # Get the correct right, bottom
        self.shown_right = self.shown_left - self.shown_width if self.shown_reflected \
                           else self.shown_left + self.shown_width
        self.shown_bottom = self.shown_top + self.shown_height

        # Extract rotation angle
        abs_sin_theta = -b / scale_y
        abs_cos_theta = d / scale_y
        self.shown_angle = math.degrees(math.atan2(abs_sin_theta, abs_cos_theta))

    def get_zone(self, mouse_position) -> zone_areas:
        '''
        Get the zone_area above which the mouse event happened
        '''
        # Undo the rotation for the mouse coordinates
        angle_radians = math.radians(-self.shown_angle)
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        rotated_x = cos_angle * (mouse_position.x() - self.shown_left) - sin_angle * (mouse_position.y() - self.shown_top) + self.shown_left
        rotated_y = sin_angle * (mouse_position.x() - self.shown_left) + cos_angle * (mouse_position.y() - self.shown_top) + self.shown_top

        # Check if the mouse is insde the circle
        circle_center_x = (self.shown_left + self.shown_right) / 2
        circle_center_y = self.shown_top - self.circle_radius - self.circle_top_offset

        distance_to_circle = math.sqrt((rotated_x - circle_center_x) ** 2 + (rotated_y - circle_center_y) ** 2)
        if distance_to_circle <= self.circle_radius + self.circle_clickable_radius:
            return zone_areas.circle

        # Check if the mouse is on top of one of the borders
        left = self.shown_left
        top = self.shown_top
        right = self.shown_right
        bottom = self.shown_bottom
        if abs(left - rotated_x) <= self.resize_clickable_border and \
           abs(top - rotated_y) <= self.resize_clickable_border:
            return zone_areas.top_left
        elif abs(right - rotated_x) <= self.resize_clickable_border and \
             abs(top - rotated_y) <= self.resize_clickable_border:
            return zone_areas.top_right
        elif abs(left - rotated_x) <= self.resize_clickable_border and \
             abs(bottom - rotated_y) <= self.resize_clickable_border:
            return zone_areas.bottom_left
        elif abs(right - rotated_x) <= self.resize_clickable_border and \
             abs(bottom - rotated_y) <= self.resize_clickable_border:
            return zone_areas.bottom_right
        elif abs(left - rotated_x) <= self.resize_clickable_border and \
            top <= rotated_y <= bottom:
            return zone_areas.left
        elif abs(right - rotated_x) <= self.resize_clickable_border and \
            top <= rotated_y <= bottom:
            return zone_areas.right
        elif abs(top - rotated_y) <= self.resize_clickable_border and \
            min(left, right) <= rotated_x <= max(left, right):
            return zone_areas.top
        elif abs(bottom - rotated_y) <= self.resize_clickable_border and \
            min(left, right) <= rotated_x <= max(left, right):
            return zone_areas.bottom

        # Check if the mouse is inside the rectangle
        if top <= rotated_y <= bottom and \
            min(left, right) <= rotated_x <= max(left, right):
            return zone_areas.center

        # By default return zone_areas.outside i.e. the mouse is not above anything
        return zone_areas.outside

    def update_cursor(self, zone:zone_areas) -> None:
        # Change the cursor shape depending on the zone
        if zone == zone_areas.circle:
            self.setCursor(QCursor(Qt.ClosedHandCursor))
        elif zone == zone_areas.top_left or zone == zone_areas.bottom_right:
            self.setCursor(QCursor(Qt.SizeFDiagCursor)) # Diagonal resize ↘↖
        elif zone == zone_areas.top_right or zone == zone_areas.bottom_left:
            self.setCursor(QCursor(Qt.SizeBDiagCursor)) # Diagonal resize ↙↗
        elif zone == zone_areas.left or zone == zone_areas.right:
            self.setCursor(QCursor(Qt.SizeHorCursor)) # Horizontal resize ↔
        elif zone == zone_areas.top or zone == zone_areas.bottom:
            self.setCursor(QCursor(Qt.SizeVerCursor)) # Vertical resize ↕
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def get_angle_from_center(self, mouse_position:QPoint) -> float:
        '''
        Returns the angle in degrees between the center of the box and the mouse position
        '''
        dx = mouse_position.x() - self.shown_center_x_original
        dy = mouse_position.y() - self.shown_center_y_original
        angle = (math.degrees(math.atan2(dy, dx)) % 360)  # Calculate the angle in degrees
        return angle

    def get_shown_center(self) -> Tuple[float, float]:
        '''
        Get the shown center coodrinates
        '''
        angle_radians = math.radians(self.shown_angle)
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        # Use (left, top) and add a rotated version of the vector (width, height)/2
        wh_vector = [(self.shown_right - self.shown_left) / 2,
                     (self.shown_bottom - self.shown_top) / 2]
        self.shown_center_x_original = self.shown_left + cos_angle * wh_vector[0] - sin_angle * wh_vector[1]
        self.shown_center_y_original = self.shown_top + sin_angle * wh_vector[0] + cos_angle * wh_vector[1]
        return (self.shown_center_x_original, self.shown_center_y_original)

    def get_original_shown_borders(self) -> Tuple[float, float, float, float]:
        '''
        Get the original borders (left, top, right, bottom) of the box drawn in shown_coordinates
        before applying the rotation around (left, top)
        '''
        self.shown_original_left = self.shown_left
        self.shown_original_top = self.shown_top
        self.shown_original_right = self.shown_right
        self.shown_original_bottom = self.shown_bottom

        return self.shown_original_left, self.shown_original_top, \
               self.shown_original_right, self.shown_original_bottom