from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt
import os
from src.utils import Box

class DraggableBox(QFrame):

    # Sginal that sends changes to the screenshot selection
    signal_selection_change = pyqtSignal()

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
            new_position = self.mapToParent(event.pos() - self.offset)
            self.move(new_position)
            # Update the selection
            self.update_selection()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = None

    def update_selection(self):
        '''
        Update the selection based on the current position and size of the draggable box
        '''
        # Get the current geometry of the box
        geometry = self.geometry()
        self.selection = Box(geometry.x(), geometry.y(), geometry.width(), geometry.height())
        # Emit the updated selection
        self.signal_selection_change.emit()

    def on_change_selection(self, selection:Box):
        '''
        Handle change of the screenshot selection from outside (e.g. from ScreenshotApp)
        '''
        self.selection = selection
        self.setGeometry(self.selection.left,
                         self.selection.top,
                         self.selection.width,
                         self.selection.height)