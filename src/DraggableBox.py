from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt

class DraggableBox(QFrame):
    def __init__(self, parent=None, preset=None):
        super().__init__(parent)
        self.initGUI()
        self.draggin = False
        self.offset = None

    def initGUI(self):
        '''
        Initialise the GUI
        '''
        self.setGeometry(50, 50, 100, 100)
        self.setStyleSheet("background-color: transparent; border: 2px solid red;")
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
