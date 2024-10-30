from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton
import cv2
import numpy as np
from functools import partial
from typing import List, Tuple

class PencilTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)
        self.points = [] # store the last 4 points
        self.pencil_color = self.config['options']['pencil_color']
        self.pencil_thickness = self.config['options']['pencil_thickness']

    def create_ui(self):
        """Create the button for the pencil tool."""
        self.button = QPushButton('Draw')
        self.button.clicked.connect(partial(self.set_tool))
        return self.button

    def on_mouse_down(self, x: int, y: int):
        self.points = [(x, y)]

    def on_mouse_move(self, x: int, y: int):
        # Add the current point to the points list
        self.points.append((x, y))
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

    def on_mouse_up(self, x: int, y: int):
        # Clear points to end the current line
        self.points = []

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