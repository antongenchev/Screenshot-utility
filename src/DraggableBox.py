from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
import os
from enum import IntEnum, auto
from src.utils import Box
from src.config import *

class zone_areas(IntEnum):
    center = 0
    left = auto()
    top = auto()
    right = auto()
    bottom = auto()
    top_left = auto()
    top_right = auto()
    bottom_left = auto()
    bottom_right = auto()

class DraggableBox(QFrame):

    # Sginal that sends changes to the screenshot selection
    signal_selection_change = pyqtSignal()

    def __init__(self, parent=None, preset=None, selection=None):
        super().__init__(parent)
        self.draggin = False
        self.resizing = False
        self.offset = None
        self.border = config['draggable_box']['border']
        self.resize_border = config['draggable_box']['resize_border']
        if selection is None:
            self.selection = Box(int(config['monitor']['width']) // 2 - 50,
                             int(config['monitor']['height']) // 2 - 50,
                             100,
                             100)
        else:
            self.selection = selection
        self.initGUI()

    def initGUI(self):
        '''
        Initialise the GUI
        '''
        self.setGeometry(self.selection.left - self.border,
                         self.selection.top - self.border,
                         self.selection.width + 2 * self.border,
                         self.selection.height + 2 * self.border)
        self.setStyleSheet(f"background-color: transparent; border: {self.border}px solid red;")
        self.setMouseTracking(True)
        self.dragging = False # are we dragging the box
        self.offset = None # position of mouse within the box on the start of dragging

    def mousePressEvent(self, event):
        '''
        On mouse down start dragging the box
        '''
        if event.button() == Qt.LeftButton:
            mouse_position = event.pos()
            zone_clicked = self.get_zone(mouse_position)
            if zone_clicked == zone_areas.center:
                # Drag the box
                self.dragging = True
                self.offset = mouse_position
            else:
                # Resize the box
                self.resizing = True
                self.resize_zone = zone_clicked

    def mouseMoveEvent(self, event):
        '''
        When dragging move the box
        '''
        if self.dragging:
            new_position = self.mapToParent(event.pos() - self.offset)
            self.move(new_position)
            # Update the selection
            self.update_selection()
        elif self.resizing:
            self.resize_box(event.pos())
        else:
            self.update_cursor(self.get_zone(event.pos()))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = None
            self.resizing = False
            self.resize_zone = None

    def update_selection(self):
        '''
        Update the selection based on the current position and size of the draggable box
        '''
        # Get the current geometry of the box
        geometry = self.geometry()
        self.selection = Box(geometry.x() + self.border,
                             geometry.y() + self.border,
                             geometry.width() - 2 * self.border,
                             geometry.height() - 2 * self.border)
        # Emit the updated selection
        self.signal_selection_change.emit()

    def on_change_selection(self, selection:Box):
        '''
        Handle change of the screenshot selection from outside (e.g. from ScreenshotApp)
        '''
        self.selection = selection
        self.setGeometry(self.selection.left - self.border,
                         self.selection.top - self.border,
                         self.selection.width + 2 * self.border,
                         self.selection.height + 2 * self.border)

    def get_zone(self, mouse_position) -> zone_areas:
        rect = self.rect()
        if (rect.left() <= mouse_position.x() <= rect.left() + self.resize_border and
            rect.top() <= mouse_position.y() <= rect.top() + self.resize_border):
            return zone_areas.top_left
        elif (rect.right() >= mouse_position.x() >= rect.right() - self.resize_border and
            rect.top() <= mouse_position.y() <= rect.top() + self.resize_border):
            return zone_areas.top_right
        elif (rect.left() <= mouse_position.x() <= rect.left() + self.resize_border and
            rect.bottom() >= mouse_position.y() >= rect.bottom() - self.resize_border):
            return zone_areas.bottom_left
        elif (rect.right() >= mouse_position.x() >= rect.right() - self.resize_border and
            rect.bottom() >= mouse_position.y() >= rect.bottom() - self.resize_border):
            return zone_areas.bottom_right
        elif rect.left() <= mouse_position.x() <= rect.left() + self.resize_border:
            return zone_areas.left
        elif rect.right() >= mouse_position.x() >= rect.right() - self.resize_border:
            return zone_areas.right
        elif rect.top() <= mouse_position.y() <= rect.top() + self.resize_border:
            return zone_areas.top
        elif rect.bottom() >= mouse_position.y() >= rect.bottom() - self.resize_border:
            return zone_areas.bottom
        else:
            return zone_areas.center

    def update_cursor(self, zone):
        # Change the cursor shape depending on the zone
        if zone == zone_areas.top_left or zone == zone_areas.bottom_right:
            self.setCursor(QCursor(Qt.SizeFDiagCursor)) # Diagonal resize ↘↖
        elif zone == zone_areas.top_right or zone == zone_areas.bottom_left:
            self.setCursor(QCursor(Qt.SizeBDiagCursor)) # Diagonal resize ↙↗
        elif zone == zone_areas.left or zone == zone_areas.right:
            self.setCursor(QCursor(Qt.SizeHorCursor)) # Horizontal resize ↔
        elif zone == zone_areas.top or zone == zone_areas.bottom:
            self.setCursor(QCursor(Qt.SizeVerCursor)) # Vertical resize ↕
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def resize_box(self, mouse_position):
        geometry = self.geometry()
        mouse_position = self.mapToParent(mouse_position)
        left, top = geometry.left(), geometry.top()
        right, bottom = geometry.left() + geometry.width(), geometry.top() + geometry.height()
        min_width, min_height = 1 + 2 * self.border, 1 + 2 * self.border # enforce min_width, min_height
         # Handle horizontal resizing (left/right)
        if self.resize_zone in [zone_areas.left, zone_areas.top_left, zone_areas.bottom_left]:
            if right - mouse_position.x() >= min_width:
                left = mouse_position.x()
            else:
                left = right - min_width
        elif self.resize_zone in [zone_areas.right, zone_areas.top_right, zone_areas.bottom_right]:
            if mouse_position.x() - left >= min_width:
                right = mouse_position.x()
            else:
                right = left + min_width
        # Handle vertical resizing (top/bottom)
        if self.resize_zone in [zone_areas.top, zone_areas.top_left, zone_areas.top_right]:
            if bottom - mouse_position.y() >= min_height:
                top = mouse_position.y()
            else:
                top = bottom - min_height
        elif self.resize_zone in [zone_areas.bottom, zone_areas.bottom_left, zone_areas.bottom_right]:
            if mouse_position.y() - top >= min_height:
                bottom = mouse_position.y()
            else:
                bottom = top + min_height
        self.setGeometry(left, top, right - left, bottom - top)
        self.update_selection()