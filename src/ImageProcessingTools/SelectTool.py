from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton, QWidget
from functools import partial
import cv2
import numpy as np
from enum import IntEnum, auto
from src.DrawableElement import DrawableElement

class SelectTool(ImageProcessingTool):

    class operation(IntEnum):
        move = 0
        resize = auto()
        rotate = auto()
        reflect = auto()
        custom = auto()

    def __init__(self, image_processor):
        super().__init__(image_processor)
        self.selected_element:DrawableElement = None
        self.current_operation:self.operation = None
        self.last_dragging_pos = None # The last mouse coordinages when dragging the mouse. (x, y)

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
        self.selected_element = self.image_processor.get_touch_element(x, y, 0)
        if self.selected_element is None:
            return
        # Get the touch_mask and transformation for the drawable element
        mask = self.selected_element.touch_mask
        transformation = self.selected_element.get_transformation()
        delta_x, delta_y = self.selected_element.offset

        # Detect the border of the white area in the touch_mask
        edges = cv2.Canny(mask, 100, 200)

        edges_img = np.zeros((*mask.shape, 4), dtype=np.uint8)
        edges_img[edges > 0] = (0, 255, 0, 255)

        h, w = mask.shape
        self.image_processor.fake_layer.final_image[delta_y:delta_y + h, delta_x:delta_x + w] =  cv2.add(
            self.image_processor.fake_layer.final_image[delta_y:delta_y + h, delta_x:delta_x + w], edges_img
        )
        self.image_processor.update_zoomable_label()

        # Handle the start of moving the element
        self.last_dragging_pos = (x, y)

    def on_mouse_move(self, x: int, y: int):
        '''
        Handle mouse move events

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        if self.selected_element is not None and self.last_dragging_pos is not None:
            # Calculate the difference in mouse movement
            dx = x - self.last_dragging_pos[0]
            dy = y - self.last_dragging_pos[1]
            # Update the offset of the selected element
            self.selected_element.transformation[0, 2] += dx
            self.selected_element.transformation[1, 2] += dy
            # Update the drawable element
            self.image_processor.apply_element_transformation(self.selected_element)
            # Update the displayed image to reflect the new position
            self.image_processor.update_zoomable_label()
            # Update last dragging position to the current position
            self.last_dragging_pos = (x, y)

    def on_mouse_up(self, x: int, y: int):
        '''
        Handle mouse move release events

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        self.is_moving_element = False
        self.dragging_start = None