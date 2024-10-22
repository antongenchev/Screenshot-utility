import os
from typing import List
from PyQt5.QtCore import Qt, QObject, QEvent, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QShortcut
from src.DraggableBox import DraggableBox
from src.OverlayWidget import OverlayWidget
from src.Memento import Memento
from src.Caretaker import caretaker
from src.utils import Box
from src.config import *

class TransparentWindow(QMainWindow):

    signal_selection_change = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_drawing = False # True if we are creating a new draggable widget
        self.start_pos = None
        self.end_pos = None

        # Create a widget which selects the area of the screenshot to save
        self.draggable_widget = DraggableBox(self, instance_TransparentWindow=self)
        self.draggable_widget.installEventFilter(self)

        self.overlay = OverlayWidget(self)
        self.overlay.setGeometry(self.rect()) # Set the geometry to match the main window
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

        # Define the keyboard shortcuts
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undo_shortcut.activated.connect(self.undo_action)
        self.redo_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        self.redo_shortcut.activated.connect(self.redo_action)

    def mousePressEvent(self, event, event_pos=None):
        '''
        Handle the mouse press event.
        ctrl + left click => start drawing a rectangle/selection/DraggableBox

        Parameters:
            event: the Qt event
            event_pos: usually None. If the event is coming from outside the TransparentWindow make it relative to the coordinates of Transp.Window
        '''
        if event.button() == Qt.LeftButton:
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                event_pos = event.pos() if event_pos is None else event_pos
                self.start_pos = event_pos # The first corner of the box
                self.overlay.start_pos = event_pos
                self.is_drawing = True
                self.overlay.is_drawing = True

                # Destory the existing draggable widget if it exists
                if self.draggable_widget:
                    # self.draggable_widget.deleteLater()
                    # self.draggable_widget = None
                    pass

    def mouseMoveEvent(self, event, event_pos=None):
        '''
        Handle mouse movements
        self.is_drawing => change the rectangle being drawn

        Parameters:
            event: the Qt event
            event_pos: usually None. If the event is coming from outside the TransparentWindow make it relative to the coordinates of Transp.Window
        '''
        if self.is_drawing:
            event_pos = event.pos() if event_pos is None else event_pos
            self.end_pos = event_pos # Track the other corner of the box
            self.overlay.end_pos = self.end_pos
            self.overlay.update()

    def mouseReleaseEvent(self, event, event_pos=None):
        '''
        Handle mouse release events
        self.is_drawing and left release => Make a new DraggableBox
        '''
        if event.button() == Qt.LeftButton and self.is_drawing:
            event_pos = event.pos() if event_pos is None else event_pos
            self.end_pos = event_pos
            self.overlay.end_pos = event_pos
            # Create the new draggable widget
            if self.start_pos and self.end_pos:
                self.create_draggable_widget()
        self.is_drawing = False
        self.overlay.is_drawing = False

    def eventFilter(self, obj, event):
        if obj == self.draggable_widget:
            if QApplication.keyboardModifiers() == Qt.ControlModifier or self.is_drawing:
                if event.type() == QEvent.MouseButtonPress:
                    event_pos = self.mapFromGlobal(obj.mapToGlobal(event.pos()))
                    self.mousePressEvent(event, event_pos=event_pos)
                    return True
                elif event.type() == QEvent.MouseMove:
                    event_pos = self.mapFromGlobal(obj.mapToGlobal(event.pos()))
                    self.mouseMoveEvent(event, event_pos=event_pos)
                elif event.type() == QEvent.MouseButtonRelease:
                    event_pos = self.mapFromGlobal(obj.mapToGlobal(event.pos()))
                    self.mouseReleaseEvent(event, event_pos=event_pos)
        return super().eventFilter(obj, event)

    def create_draggable_widget(self):
        # Calculate the position and size of the new DraggableBox
        left = min(self.start_pos.x(), self.end_pos.x())
        top = min(self.start_pos.y(), self.end_pos.y())
        width = abs(self.start_pos.x() - self.end_pos.x())
        height = abs(self.start_pos.y() - self.end_pos.y())
        if width == 0 or height == 0:
            # Can not create a DraggableBox with size 
            return None
        selection = Box(left, top, width, height)
        self.set_draggable_widget(selection)
        # Save the state
        self.save_memento()

    def set_draggable_widget(self, selection:Box):
        '''
        Set draggable widget with a given screenshot selection
        '''
        if self.draggable_widget:
            # Change the selection of the existing DraggableBox
            self.draggable_widget.on_change_selection(selection)
        else:
            # Create the new DraggableBox
            self.draggable_widget = DraggableBox(self, selection=selection, instance_TransparentWindow=self)
            self.draggable_widget.installEventFilter(self)
            self.draggable_widget.show()
        self.signal_selection_change.emit()

    def undo_action(self):
        '''
        Perform undo action. Load the previous memento
        '''
        memento = caretaker.undo('TransparentWindow')
        if memento:
            self.load_memento(memento)

    def redo_action(self):
        '''
        Perform redo action. Load the redo memento
        '''
        memento = caretaker.redo('TransparentWindow')
        if memento:
            self.load_memento(memento)

    def save_memento(self) -> Memento:
        '''
        Return a memento with the state of the current Transparent Window
        '''
        memento = Memento(selection=self.draggable_widget.selection)
        caretaker.save('TransparentWindow', memento)

    def load_memento(self, m:Memento) -> None:
        '''
        Load a Memento
        '''
        self.set_draggable_widget(m.selection)
