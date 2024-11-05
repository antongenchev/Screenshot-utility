from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
import cv2
import numpy as np
from enum import IntEnum, auto
import importlib
from typing import List
from scipy.interpolate import CubicSpline
from src.ZoomableLabel import ZoomableLabel
from src.Layer import Layer
from src.DrawableElement import DrawableElement
from src.config import config

# Import ImageProcessingTools
from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from src.ImageProcessingTools.PencilTool import PencilTool

class ImageProcessor(QWidget):

    # The available image processing tools
    class tools(IntEnum):
        move = 0
        pencil = auto()

    def __init__(self, zoomable_label):
        super().__init__()
        self.zoomable_label = zoomable_label
        self.zoomable_label:ZoomableLabel
        self.current_tool = None
        self.tool_classes = {}
        self.layers = [] # All the layers
        self.fake_layer = None # layer for visualising stuff not part of what is drawn
        self.active_layer_index = 0 # the index of the active layer
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Load tools from the config.json file
        self.load_tools_from_config()

        for tool_name in sorted(self.tool_classes.keys(), key=lambda k: self.tool_classes[k]['order']):
            tool_obj = self.tool_classes[tool_name]['object']
            tool_widget = tool_obj.create_ui()
            layout.addWidget(tool_widget)

        self.setLayout(layout)

    def load_tools_from_config(self):
        for tool in config['tools']:
            tool_name = tool["name"]
            module = importlib.import_module(f'src.ImageProcessingTools.{tool_name}')
            tool_class = getattr(module, tool_name)
            tool_obj = tool_class(self)
            self.tool_classes[tool_name] = {
                'class': tool_class,
                'object': tool_obj,
                'order': tool['order'],
            }

    def set_tool(self, tool: ImageProcessingTool):
        self.current_tool = tool

    def on_mouse_move(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel.

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        self.current_tool.on_mouse_move(x, y)

    def on_mouse_down(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel for left mouse button down event

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        self.current_tool.on_mouse_down(x, y)

    def on_mouse_up(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel for left mouse button release event

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        self.current_tool.on_mouse_up(x, y)

    #################
    # Layer methods #
    #################

    def add_layer(self, image=None):
        layer = Layer(image=image)
        self.layers.append(layer)
        self.active_layer_index = len(self.layers) - 1

    def remove_layer(self, index):
        if 0 <= index < len(self.layers):
            del self.layers[index]
            self.active_layer_index = min(self.active_layer_index, len(self.layers) - 1)

    def set_active_layer(self, index):
        if 0 <= index < len(self.layers):
            self.active_layer_index = index

    def toggle_layer_visibility(self, index):
        if 0 <= index < len(self.layers):
            self.layers[index].toggle_visibility()

    def render_layers(self):
        '''
        Render all layers
        '''
        self.zoomable_label.update_transformed_image()

    def render_layer(self, index:int) -> None:
        '''
        Render the layer with index `index`.
        That is update the final_image of the layer

        Parameters:
            index: the index of the layer in self.layers
        '''
        layer = self.layers[index]
        for drawable_element in layer.elements:
            self.render_element(self, drawable_element)
            # add element to layer

    ###################
    # Element methods #
    ###################

    def render_element(self, drawable_element:DrawableElement):
        tool_name = drawable_element.tool
        tool_obj = self.tool_classes[tool_name]['object']
        tool_obj.draw_drawable_element(drawable_element)

    def add_element(self, drawable_element:DrawableElement):
        self.layers[self.active_layer_index].add_element(drawable_element)