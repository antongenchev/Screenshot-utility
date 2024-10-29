from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton
import cv2
from functools import partial

class PencilTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)

    def create_ui(self):
        """Create the button for the pencil tool."""
        self.button = QPushButton('Draw')
        self.button.clicked.connect(partial(self.enable))
        return self.button

    def on_mouse_press(self, x: int, y: int):
        pass

    def on_mouse_move(self, x: int, y: int):
        # Apply drawing on the image at the (x, y) location
        color = (255, 0, 0)  # Red color for example
        thickness = 5  # Example thickness
        cv2.circle(self.zoomable_label.transformed_image, (x, y), thickness, color, -1)
        # Update the ZoomableLabel with the modified image
        self.zoomable_label.update_transformed_image()

    def on_mouse_release(self, x: int, y: int):
        pass
