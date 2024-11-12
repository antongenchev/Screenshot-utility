from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton, QWidget
from functools import partial
import cv2
import numpy as np

class SelectTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)

    def create_ui(self):
        """Create the button for the move tool."""
        self.button = QPushButton('Select')
        self.button.clicked.connect(partial(self.set_tool))
        return self.button

    def create_settings_ui(self):
        return QWidget()

    def set_tool(self):
        super().set_tool()

    def on_mouse_down(self, x: int, y: int):
        '''
        Handle mouse down events. Try to select a drawable element from the active layer

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        # Get the drawable element beneath the mouse down event if it such an element exists
        drawable_element = self.image_processor.get_touch_element(x, y, 0)
        if drawable_element is None:
            return
        # Get the touch_mask and offset for the drawable element
        mask = drawable_element.touch_mask
        delta_x, delta_y = drawable_element.offset

        # Detect the border of the white area in the touch_mask
        edges = cv2.Canny(mask, 100, 200)

        edges_img = np.zeros((*mask.shape, 4), dtype=np.uint8)
        edges_img[edges > 0] = (0, 255, 0, 255)

        h, w = mask.shape
        self.image_processor.fake_layer.final_image[delta_y:delta_y + h, delta_x:delta_x + w] =  cv2.add(
            self.image_processor.fake_layer.final_image[delta_y:delta_y + h, delta_x:delta_x + w], edges_img
        )
        self.image_processor.update_zoomable_label()


    def on_mouse_move(self, x: int, y: int):
        '''
        Handle mouse move events

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        pass

    def on_mouse_up(self, x: int, y: int):
        '''
        Handle mouse move release events

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        pass