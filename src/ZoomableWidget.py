from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedLayout
from PyQt5.QtCore import Qt
from src.ZoomableLabel import ZoomableLabel

class Overlay(QWidget):
    def __init__(self, parent, target):
        super().__init__(parent)
        self.target = target # The target widget to forward events to
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
        # Ensure the overlay resizes with its parent
        self.resize(self.parentWidget().size())

class ZoomableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QStackedLayout(self)
        layout.setStackingMode(QStackedLayout.StackAll)

        # Create the ZoomableLabel
        self.zoomable_label = ZoomableLabel(self)
        layout.addWidget(self.zoomable_label)

        # Create the Overlay
        self.overlay = Overlay(self, self.zoomable_label)
        layout.addWidget(self.overlay)

        # Make the overlay invsible
        self.overlay.setStyleSheet("background: transparent;")