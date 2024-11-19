from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedLayout
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect
from src.ZoomableLabel import ZoomableLabel

class Overlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.target = parent.zoomable_label # The target widget to forward events to
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.target.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.target.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.target.mouseReleaseEvent(event)

    def wheelEvent(self, event):
        self.target.wheelEvent(event)

    def resizeEvent(self, event):
        # Ensure the overlay resizes with its parent (ZoomableWidget)
        super().resizeEvent(event)

class ZoomableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QStackedLayout(self)
        layout.setStackingMode(QStackedLayout.StackAll)

        # Create the ZoomableLabel
        self.zoomable_label = ZoomableLabel(self)
        self.zoomable_label.setFixedSize(600, 400)  # Set some default size
        self.zoomable_label.setStyleSheet("border: 1px solid black")
        layout.addWidget(self.zoomable_label)

        # Create the Overlay
        self.overlay = Overlay(self)
        self.overlay.setGeometry(self.zoomable_label.geometry())
        layout.addWidget(self.overlay)

        # Make the overlay invsible
        self.overlay.setStyleSheet("background: transparent;")
        # Make the overlay above the ZoomableLabel
        self.overlay.raise_()

    def resizeEvent(self, event):
        # Resize the overlay to match the ZoomableLabel's size when ZoomableWidget is resized
        self.overlay.setGeometry(self.zoomable_label.geometry())
        super().resizeEvent(event)