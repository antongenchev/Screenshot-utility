import os
from PyQt5.QtCore import Qt, QObject, QEvent
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from src.DraggableBox import DraggableBox
from src.utils import Box
from src.config import *

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_ctrl = False # True if we are creating a new draggable widget
        # Create a widget which selects the are of the screenshot to save
        self.draggable_widget = DraggableBox(self)
        self.draggable_widget.installEventFilter(self)

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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                print("Mouse Pressed with Ctrl")

    def mouseMoveEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            print("Dragging with Ctrl")
            self.is_ctrl = True
        else:
            self.is_ctrl = False

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("Release with Ctrl")
        self.is_ctrl = False

    def eventFilter(self, obj, event):
        if obj == self.draggable_widget:
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                if event.type() in [QEvent.MouseButtonPress, QEvent.MouseMove, QEvent.MouseButtonRelease]:
                    self.mousePressEvent(event)
                    return True
        return super().eventFilter(obj, event)