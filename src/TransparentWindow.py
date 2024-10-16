import os
from PyQt5.QtCore import Qt, QObject, QEvent, QRect
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from src.DraggableBox import DraggableBox
from src.OverlayWidget import OverlayWidget
from src.utils import Box
from src.config import *

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_drawing = False # True if we are creating a new draggable widget
        self.start_pos = None
        self.end_pos = None
        # Create a widget which selects the area of the screenshot to save
        self.draggable_widget = DraggableBox(self)
        self.draggable_widget.installEventFilter(self)
        # self.draggable_widget = None
        self.overlay = OverlayWidget(self)
        self.overlay.setGeometry(self.rect())  # Set the geometry to match the main window
        self.overlay.show()

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
                self.start_pos = event.pos() # The first corner of the box
                self.overlay.start_pos = event.pos()
                self.is_drawing = True
                self.overlay.is_drawing = True

                # Destory the existing draggable widget if it exists
                if self.draggable_widget:
                    self.draggable_widget.deleteLater()
                    self.draggable_widget = None

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_pos = event.pos() # Track the other corner of the box
            self.overlay.end_pos = self.end_pos
            self.overlay.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.end_pos = event.pos()
            self.overlay.end_pos = event.pos()
            # Create the new draggable widget
            if self.start_pos and self.end_pos:
                self.create_draggable_widget()
        self.is_drawing = False
        self.overlay.is_drawing = False

    def eventFilter(self, obj, event):
        if obj == self.draggable_widget:
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                if event.type() in [QEvent.MouseButtonPress, QEvent.MouseMove, QEvent.MouseButtonRelease]:
                    self.mousePressEvent(event)
                    return True
        return super().eventFilter(obj, event)

    def create_draggable_widget(self):
        print(self.start_pos, self.end_pos)
        left = min(self.start_pos.x(), self.end_pos.x())
        top = min(self.start_pos.y(), self.end_pos.y())
        width = abs(self.start_pos.x() - self.end_pos.x())
        height = abs(self.start_pos.y() - self.end_pos.y())
        if width == 0 or height == 0:
            # Can not create a DraggableBox with size 
            return None
        selection = Box(left, top, width, height)
        self.draggable_widget = DraggableBox(self, selection=selection)
        self.draggable_widget.installEventFilter(self)
        self.draggable_widget.show()