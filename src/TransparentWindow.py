import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        '''
        Initialise the gui of the screenshot.
        This is a transparent window whose background is a screenshot
        '''
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Create a widget which takes the whole space and has background=screenshot
        self.screenshot_widget =  QWidget(self)
        self.screenshot_widget.setStyleSheet(f"background-image: url('{os.getenv('SCREENSHOT_BACKGROUND')}'); background-repeat: no-repeat;")
        self.setCentralWidget(self.screenshot_widget)