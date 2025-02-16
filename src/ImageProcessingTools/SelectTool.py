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

    def disable(self) -> None:
        '''
        Overide of the disable function from the ImageProcessingTool to remove the RotatableBoxes.
        '''
        # Clear the rotatable boxes / selections when switching to another tool.
        self.delete_rotatable_boxes()
        super().disable()

    def on_mouse_down(self, x: int, y: int):
        '''
        Handle mouse down events. Try to select a drawable element from the active layer

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        # Check if there's a previously created rotatable_box and delete it if it exists
        self.delete_rotatable_boxes()

        # Get the drawable element beneath the mouse down event if such an element exists
        self.selected_element = self.image_processor.get_touch_element(x, y, 0)
        if self.selected_element is None:
            return

        # Create a rotatable box in the overlay of the zoomable widget
        rotatable_box = RotatableBox(
            parent=self.image_processor.zoomable_widget.overlay,
            zoomable_widget=self.image_processor.zoomable_widget,
            image_processor=self.image_processor,
            drawable_element=self.selected_element
        )
        self.image_processor.zoomable_widget.overlay.rotatable_box = rotatable_box

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

    def delete_rotatable_boxes(self):
        '''
        Use to delete the rotatable box if such exists.
        '''
        # Check if there's a previously created rotatable_box and delete it if it exists
        if hasattr(self.image_processor.zoomable_widget.overlay, 'rotatable_box') \
        and self.image_processor.zoomable_widget.overlay.rotatable_box is not None:
                rotatable_box = self.image_processor.zoomable_widget.overlay.rotatable_box
                rotatable_box.setParent(None)
                rotatable_box.deleteLater()
                self.image_processor.zoomable_widget.overlay.rotatable_box = None