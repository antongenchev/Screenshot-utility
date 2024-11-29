from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton, QWidget
from functools import partial
import cv2
import numpy as np
from enum import IntEnum, auto
from src.DrawableElement import DrawableElement
from src.RotatableBox import RotatableBox

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

        # Create a rotatable box in the overlay of the zoomable widget
        self.image_processor.zoomable_widget.overlay.rotatable_box = RotatableBox(
            parent=self.image_processor.zoomable_widget.overlay,
            zoomable_widget=self.image_processor.zoomable_widget,
            image_processor=self.image_processor,
            drawable_element=self.selected_element
        )

    def on_mouse_move(self, x: int, y: int):
        '''
        Handle mouse move events

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''

    def on_mouse_up(self, x: int, y: int):
        '''
        Handle mouse move release events

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''