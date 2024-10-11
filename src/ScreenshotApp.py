from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit, QSpinBox, QLabel
from src.TransparentWindow import TransparentWindow
from mss import mss
from PIL import Image
import os
from src.utils import Box

class ScreenshotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initGUI()

    def initGUI(self):
        '''
        Initialise the GUI
        '''
        self.layout = QVBoxLayout()
        self.setWindowTitle('Screenshot Taker')
        self.setGeometry(2920, 300, 400, 400) # Where to start the app: position (2930, 300) on the screen

        self.transparent_window = None # Transparent window object

        # Buttons for taking and closing screenshot
        h_layout = QHBoxLayout()
        self.button_screenshot = QPushButton('Take a new screenshot', self)
        self.button_screenshot.clicked.connect(self.on_take_screenshot)
        self.button_close_screenshot = QPushButton('Close screenshot', self)
        self.button_close_screenshot.clicked.connect(self.on_close_screenshot)
        h_layout.addWidget(self.button_screenshot)
        h_layout.addWidget(self.button_close_screenshot)
        self.layout.addLayout(h_layout)

        # Menu for changing the screenshot selection
        grid_layout = QGridLayout()
        self.label_position = QLabel('Position(x,y)')
        self.field_left = QSpinBox(self)
        self.field_top = QSpinBox(self)
        self.label_size = QLabel('Size(w,h)')
        self.field_width = QSpinBox(self)
        self.field_height = QSpinBox(self)
        grid_layout.addWidget(self.label_position, 0, 0)
        grid_layout.addWidget(self.field_left, 0, 1)
        grid_layout.addWidget(self.field_top, 0, 2)
        grid_layout.addWidget(self.label_size, 1, 0)
        grid_layout.addWidget(self.field_width, 1, 1)
        grid_layout.addWidget(self.field_height, 1, 2)
        self.layout.addLayout(grid_layout)

        h_layout2 = QHBoxLayout()
        self.button_save = QPushButton('Save', self)
        self.button_save.clicked.connect(self.on_save)
        h_layout2.addWidget(self.button_save)
        self.layout.addLayout(h_layout2)

        self.setLayout(self.layout)

    def on_take_screenshot(self):

        # Take a screenhot
        with mss() as sct:
            screenshot = sct.grab({'left': 0, 'top': 0, 'width': 1920, 'height': 1080})
            screenshot = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            screenshot.save(os.getenv('SCREENSHOT_BACKGROUND'))
        # Open a windoe with the background being the screenshot
        self.transparent_window = TransparentWindow()
        self.transparent_window.show()

    def on_save(self):
        try:
            with mss() as sct:
                screenshot = sct.grab({'left':self.transparent_window.draggabe_widget.selection.left + 1,
                                       'top':self.transparent_window.draggabe_widget.selection.top + 1,
                                       'width':self.transparent_window.draggabe_widget.selection.width - 2,
                                       'height':self.transparent_window.draggabe_widget.selection.height - 2})
                screenshot = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                screenshot.save(os.getenv('SCREENSHOT_SELECTION'))
        except Exception as e:
            print(e)

    def on_close_screenshot(self):
        if self.transparent_window:
            self.transparent_window.close()
            self.transparent_window = None

    def closeEvent(self, event):
        if self.transparent_window:
            self.transparent_window.close()
        event.accept()