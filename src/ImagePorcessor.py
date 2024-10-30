from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
import cv2
import numpy as np
from enum import IntEnum, auto
import importlib
from scipy.interpolate import CubicSpline
from src.ZoomableLabel import ZoomableLabel
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
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Load tools from the config.json file
        self.load_tools_from_config()

        for tool_name in sorted(self.tool_classes.keys(), key=lambda k: self.tool_classes[k]['order']):
            tool_class = self.tool_classes[tool_name]['class']
            tool_obj = tool_class(self)
            tool_widget = tool_obj.create_ui()
            tool_obj.enable()
            layout.addWidget(tool_widget)

        self.setLayout(layout)

    def load_tools_from_config(self):
        for tool in config['tools']:
            tool_name = tool["name"]
            module = importlib.import_module(f'src.ImageProcessingTools.{tool_name}')
            tool_class = getattr(module, tool_name)
            self.tool_classes[tool_name] = {
                'class': tool_class,
                'order': tool['order']
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
