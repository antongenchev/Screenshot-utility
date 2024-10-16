from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QWidget

class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents) # Make mouse events go through
        self.setAttribute(Qt.WA_NoSystemBackground) # No background
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.start_pos = None
        self.end_pos = None
        self.is_drawing = False
        self.setMouseTracking(True) # Enable mouse tracking

    def paintEvent(self, event):
        '''
        Paint a rectangle when the user is creating a new Draggable Box
        '''
        if self.is_drawing and self.start_pos and self.end_pos:
            painter = QPainter(self)
            pen = QPen(Qt.blue, 2, Qt.SolidLine)
            painter.setPen(pen)
            rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.drawRect(rect)