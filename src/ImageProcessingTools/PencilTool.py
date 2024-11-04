from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton
import cv2
import numpy as np
from functools import partial
from typing import List, Tuple
from src.DrawableElement import DrawableElement

class PencilTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)
        self.points = [] # store the last 4 points
        self.all_points = [] # store all the points
        self.pencil_color = self.config['options']['pencil_color']
        self.pencil_thickness = self.config['options']['pencil_thickness']

    def create_ui(self):
        """Create the button for the pencil tool."""
        self.button = QPushButton('Draw')
        self.button.clicked.connect(partial(self.set_tool))
        return self.button

    def on_mouse_down(self, x: int, y: int):
        self.points = [(x, y)]
        cv2.circle(self.image_processor.zoomable_label.transformed_image,
                   (x, y),
                   radius = 0,
                   color=self.pencil_color,
                   thickness=self.pencil_thickness)
        self.image_processor.zoomable_label.update_transformed_image()

    def on_mouse_move(self, x: int, y: int):
        # Add the current point to the points list
        self.points.append((x, y))
        self.all_points.append((x, y))
        if len(self.points) >= 4:
            # Remove points older than the last 4 points
            self.points = self.points[-4:]
            # Calculate the spline points
            spline_points = self.catmull_rom_spline(*self.points)
            # Draw lines between the interpolated points
            for i in range(len(spline_points) - 1):
                cv2.line(self.image_processor.zoomable_label.transformed_image,
                         spline_points[i],
                         spline_points[i + 1],
                         color=self.pencil_color,
                         thickness=self.pencil_thickness)
            # Update the ZoomableLabel with the modified image
            self.image_processor.zoomable_label.update_transformed_image()
        elif len(self.points) == 2:
            # Draw a line between the first 2 points
            cv2.line(self.image_processor.zoomable_label.transformed_image,
                     self.points[0],
                     self.points[1],
                     color=self.pencil_color,
                     thickness=self.pencil_thickness)
            self.image_processor.zoomable_label.update_transformed_image()

    def on_mouse_up(self, x: int, y: int):
        # Clear points to end the current line
        self.points = []
        if len(self.all_points) > 0:
            instructions = {
                'points': self.all_points,
                'color': self.pencil_color,
                'thickness': self.pencil_thickness
            }
            self.create_drawable_element(instructions)
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
        Update drawable_element.image using drawable_element.instructions
        '''
        # Clear the image before drawing
        drawable_element.clear_image()

        # Get the instructions for drawing the DrawableElement
        points = drawable_element.instructions['points']
        color = drawable_element.instructions['pencil_color']
        thickness = drawable_element.instructions['pencil_thickness']

        # Draw the first point
        if len(points) >= 1:
            cv2.circle(drawable_element.image,
                       (points[0]),
                       radius = 0,
                       color=color,
                       thickness=thickness)
        # Draw the line between the 1st and 2nd point
        if len(points) >= 2:
            cv2.line(drawable_element.image,
                     points[0],
                     points[1],
                     color=color,
                     thickness=thickness)
        # Draw the rest of the interpolated points/lines
        for i in range(1, len(points) - 3):
            # draw the between points i and i+1
            spline_points = self.catmull_rom_spline(points[i-1: i+3]) # calculate the spline points
            # Draw lines between the interpolated points
            for i in range(len(spline_points) - 1):
                cv2.line(drawable_element.image,
                         spline_points[i],
                         spline_points[i + 1],
                         color=self.pencil_color,
                         thickness=self.pencil_thickness)