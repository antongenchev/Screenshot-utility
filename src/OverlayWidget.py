from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QWidget
from src.config import *

class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents) # Make mouse events go through
        self.setAttribute(Qt.WA_NoSystemBackground) # No background
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.border = config['draggable_box']['border'] # the border of the selection (not the OverlayWidget itself)
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
            pen = QPen(Qt.blue, self.border, Qt.SolidLine)
            painter.setPen(pen)
            inner_rect = QRect(self.start_pos, self.end_pos).normalized() # the inner_rect is the actual selection
            painter.setRenderHint(QPainter.Antialiasing, False)
            # Adjust the rectangle dimensions to account for the width of the rectangle
            outer_rect = QRect(inner_rect.left() - self.border // 2, inner_rect.top() - self.border // 2,
                               inner_rect.width() + self.border - 1, inner_rect.height() + self.border - 1)
            painter.drawRect(outer_rect)