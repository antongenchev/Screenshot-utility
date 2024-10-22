from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QPixmap, QImage
from PyQt5.QtCore import Qt, QPoint

class ZoomableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_pixmap = QPixmap()
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.last_mouse_pos = None

    def setPixmap(self, pixmap):
        self.original_pixmap = pixmap
        super().setPixmap(pixmap)

    def wheelEvent(self, event):
        '''
        Scale the image on scrolling the mouse: zoom in - zoom out
        '''
        factor = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.scale_factor *= factor
        self.update()

    def mousePressEvent(self, event):
        '''
        Start dragging the image
        '''
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        '''
        Handle dragging the image
        '''
        if self.last_mouse_pos is not None:
            delta = event.pos() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None

    def paintEvent(self, event):
        # Draw the scaled and translated pixmap
        painter = QPainter(self)
        scaled_pixmap = self.original_pixmap.scaled(self.original_pixmap.size() * self.scale_factor, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(self.offset, scaled_pixmap)
