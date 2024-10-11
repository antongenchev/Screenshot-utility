from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt
import os
from src.utils import Box

class DraggableBox(QFrame):
    def __init__(self, parent=None, preset=None):
        super().__init__(parent)
        self.draggin = False
        self.offset = None
        self.selection = Box(int(os.getenv('MONITOR_WIDTH')) // 2 - 50,
                             int(os.getenv('MONITOR_HEIGHT')) // 2 - 50,
                             100,
                             100)
        self.initGUI()

    def initGUI(self):
        '''
        Initialise the GUI
        '''
        self.setGeometry(self.selection.left,
                         self.selection.top,
                         self.selection.width,
                         self.selection.height)
        self.setStyleSheet("background-color: transparent; border: 1px solid red;")
        self.setMouseTracking(True)
        self.dragging = False # are we dragging the box
        self.offset = None # position of mouse within the box on the start of dragging

    def mousePressEvent(self, event):
        '''
        On mouse down start dragging the box
        '''
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        '''
        When dragging move the box
        '''
        if self.dragging and self.offset is not None:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = None
