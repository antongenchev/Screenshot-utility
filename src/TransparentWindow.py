import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget
from src.DraggableBox import DraggableBox
from src.utils import Box
from src.config import *

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        # Create a widget which selects the are of the screenshot to save
        self.draggable_widget = DraggableBox(self)

    def initUI(self):
        '''
        Initialise the gui of the screenshot.
        This is a transparent window whose background is a screenshot
        '''
        self.setGeometry(0, 0, int(config['monitor']['width']), int(config['monitor']['height']))
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Create a widget which takes the whole space and has background=screenshot
        self.screenshot_widget =  QWidget(self)
        self.screenshot_widget.setStyleSheet(f"background-image: url('{config['paths']['screenshot_background']}'); background-repeat: no-repeat;")
        self.setCentralWidget(self.screenshot_widget)

