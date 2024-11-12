from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QSlider, QLabel, QWidget, QColorDialog
from PyQt5.QtCore import Qt
import cv2
import numpy as np
from functools import partial
import copy
from typing import List, Tuple
from src.DrawableElement import DrawableElement

class PencilTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)
        self.points = [] # store the last 4 points
        self.all_points = [] # store all the points
        self.pencil_color = self.config['options']['pencil_color']
        self.pencil_thickness = self.config['options']['pencil_thickness']
        self.pencil_opacity = self.config['options']['pencil_opacity'] # in range 0-1
        self.pencil_alpha = self.pencil_opacity * 255

        self.grayscale_mask = None # a cv2 image with 1 channel. 255 => we have drawn here, 0 => we have not drawn here

    def create_ui(self):
        """Create the button for the pencil tool."""
        self.button = QPushButton('Draw')
        self.button.clicked.connect(partial(self.set_tool))
        return self.button

    def on_mouse_down(self, x: int, y: int):
        '''
        Handle mouse down events. Draw a dot

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        self.all_points = [(x, y)]
        # Create a new mask
        self.grayscale_mask = np.zeros(self.image_processor.fake_layer.final_image.shape[:2], dtype=np.uint8)
        # Draw a white dot
        cv2.circle(self.grayscale_mask,
                   (x, y),
                   radius = 0,
                   color=255, # white - a mask will be applied to change it
                   thickness=self.pencil_thickness)
        # Change white areas to the specified color with opacity
        for c in range(3): # Loop over the RGB channels
            self.image_processor.fake_layer.final_image[:, :, c] = np.where(self.grayscale_mask == 255,
                                                    self.pencil_color[c],
                                                    self.image_processor.fake_layer.final_image[:, :, c])
        self.image_processor.fake_layer.final_image[self.grayscale_mask == 255, 3] = self.pencil_alpha
        # Update the zoomable label
        self.image_processor.update_zoomable_label()

    def on_mouse_move(self, x: int, y: int):
        '''
        Draw a curve (if points are more than 4), line (points are 2), or nothing (3 points)

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        # Add the current point to the points list
        self.all_points.append((x, y))
        if len(self.all_points) >= 4:
            # Calculate the spline points
            spline_points = self.catmull_rom_spline(*self.all_points[-4:])
            # Draw lines between the interpolated points
            for i in range(len(spline_points) - 1):
                cv2.line(self.grayscale_mask,
                         spline_points[i],
                         spline_points[i + 1],
                         color=255, # white - a mask will be applied to change it
                         thickness=self.pencil_thickness)
        elif len(self.all_points) == 2:
            # Draw a line between the first 2 points
            cv2.line(self.grayscale_mask,
                     self.all_points[0],
                     self.all_points[1],
                     color=255,
                     thickness=self.pencil_thickness)
        # Update the zoomable label
        if len(self.all_points) != 3:
            # Change white areas to the specified color with opacity
            for c in range(3): # Loop over the RGB channels
                self.image_processor.fake_layer.final_image[:, :, c] = np.where(self.grayscale_mask == 255,
                                                        self.pencil_color[c],
                                                        self.image_processor.fake_layer.final_image[:, :, c])
            self.image_processor.fake_layer.final_image[self.grayscale_mask == 255, 3] = self.pencil_alpha
            self.image_processor.update_zoomable_label()

    def on_mouse_up(self, x: int, y: int):
        '''
        On a mouse release create a drawable element

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        if len(self.all_points) > 0:
            instructions = {
                'points': self.all_points,
                'color': self.pencil_color,
                'thickness': self.pencil_thickness,
                'alpha': self.pencil_alpha
            }
            drawable_element_image = copy.deepcopy(self.image_processor.fake_layer.final_image)
            self.image_processor.fake_layer.clear_final_image()
            self.create_drawable_element(instructions, drawable_element_image, touch_mask=self.grayscale_mask)
        # Clear points to end the current line
        self.all_points = []

    def catmull_rom_spline(self, p0, p1, p2, p3, num_points=100):
        """
        Calculate Catmull-Rom spline points.

        Parameters:
            p0, p1, p2, p3 - Tuples (x, y) for the control points
            num_points - Number of points to generate along the spline
        Returns:
            List of interpolated points along the Catmull-Rom spline
        """
        p0, p1, p2, p3 = np.array(p0), np.array(p1), np.array(p2), np.array(p3)
        interpolated_points = []
        # Calculate each interpolated point
        for i in range(num_points + 1):
            t = i / num_points # Parameter t ranges from 0 to 1
            # Catmull-Rom spline formula
            point = 0.5 * ((2 * p1) +
                           (-p0 + p2) * t +
                           (2*p0 - 5*p1 + 4*p2 - p3) * t**2 +
                           (-p0 + 3*p1 - 3*p2 + p3) * t**3)
            interpolated_points.append((int(point[0]), int(point[1])))
        return interpolated_points

    def draw_drawable_element(self, drawable_element:DrawableElement) -> None:
        '''
        Draw the drawable from the instructions.
        Update drawable_element.image using drawable_element.instructions.
        Note: The pencil first draws white on a cleared image. Then the white areas are 
        made non transparent and with the right color
        '''
        # Clear the image before drawing
        drawable_element.clear_image()

        # Get the instructions for drawing the DrawableElement
        points = drawable_element.instructions['points']
        color = drawable_element.instructions['color']
        thickness = drawable_element.instructions['thickness']
        alpha_value = drawable_element.instructions['alpha'] * 255

        # Draw the first point
        if len(points) >= 1:
            cv2.circle(drawable_element.image,
                       (points[0]),
                       radius = 0,
                       color=(255, 255, 255),
                       thickness=thickness)
        # Draw the line between the 1st and 2nd point
        if len(points) >= 2:
            cv2.line(drawable_element.image,
                     points[0],
                     points[1],
                     color=(255, 255, 255),
                     thickness=thickness)
        # Draw the rest of the interpolated points/lines
        for i in range(1, len(points) - 3):
            # draw the between points i and i+1
            spline_points = self.catmull_rom_spline(*points[i-1: i+3]) # calculate the spline points
            # Draw lines between the interpolated points
            for j in range(len(spline_points) - 1):
                cv2.line(drawable_element.image,
                         spline_points[j],
                         spline_points[j + 1],
                         color=(255, 255, 255),
                         thickness=thickness)
        # Create a mask for the white areas
        mask = cv2.inRange(drawable_element.image[:, :, :3], (255, 255, 255), (255, 255, 255))
        # Change white areas to the specified color with opacity
        for c in range(3): # Loop over the RGB channels
            drawable_element.image[:, :, c] = np.where(mask == 255,
                                                    color[c],
                                                    drawable_element.image[:, :, c])
        # Set the alpha channel for the white areas to the desired opacity
        drawable_element.image[mask == 255, 3] = alpha_value

    def create_settings_ui(self):
        settings_widget = QWidget()
        layout = QVBoxLayout()

        # Pencil Thickness Slider
        pencil_thickness_label = QLabel("Pencil Size")
        pencil_thickness_slider = QSlider(Qt.Horizontal)
        pencil_thickness_slider.setMinimum(1)
        pencil_thickness_slider.setMaximum(50)
        pencil_thickness_slider.setValue(self.pencil_thickness)
        pencil_thickness_slider.valueChanged.connect(self.set_pencil_thickness)
        layout.addWidget(pencil_thickness_label)
        layout.addWidget(pencil_thickness_slider)

        # Opacity Slider
        opacity_label = QLabel("Opacity %")
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setMinimum(0)
        opacity_slider.setMaximum(100)  # Set the range to 0 - 100 for better precision
        opacity_slider.setValue(int(self.pencil_opacity * 100))  # Scale initial opacity to slider range
        opacity_slider.valueChanged.connect(self.set_opacity)
        layout.addWidget(opacity_label)
        layout.addWidget(opacity_slider)

        # Color Picker Button
        color_picker_button = QPushButton("Select Pencil Color")
        color_picker_button.clicked.connect(self.open_color_picker)
        layout.addWidget(color_picker_button)

        settings_widget.setLayout(layout)
        return settings_widget

    def set_pencil_thickness(self, value):
        self.pencil_thickness = value

    def set_opacity(self, value):
        self.pencil_opacity = value / 100
        self.pencil_alpha = self.pencil_opacity * 255

    def open_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():  # Check if a valid color is selected
            # Update the pencil color to the selected color in RGB format
            self.pencil_color = (color.red(), color.green(), color.blue())