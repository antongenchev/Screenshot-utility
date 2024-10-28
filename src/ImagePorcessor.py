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
            tool_widget = tool_class(self).create_ui()
            layout.addWidget(tool_widget)
            tool_widget.clicked.connect(lambda _, t=tool_widget: self.set_tool(t))

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

    def on_pencil(self):
        self.drawing_enabled = True
        self.zoomable_label.drawing_enabled = self.drawing_enabled

    def handle_draw(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel.

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        if self.drawing_enabled:
            # Apply drawing on the image at the (x, y) location
            color = (255, 0, 0)  # Red color for example
            thickness = 5  # Example thickness
            cv2.circle(self.zoomable_label.transformed_image, (x, y), thickness, color, -1)
            # Update the ZoomableLabel with the modified image
            self.zoomable_label.update_transformed_image()

    def handle_start_draw(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel for left mouse button down event

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        pass

    def handle_stop_draw(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel for left mouse button release event

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        pass
