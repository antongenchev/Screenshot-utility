from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit, QSpinBox, QLabel
from PyQt5.QtCore import pyqtSlot
from src.TransparentWindow import TransparentWindow
from mss import mss
from PIL import Image
import os
from src.utils import Box
from src.config import *

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
        self.setGeometry(config['start_position']['left'],
                         config['start_position']['top'],
                         config['start_position']['width'],
                         config['start_position']['height'])

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
        self.field_left.setRange(0, config['monitor']['width'])
        self.field_top.setRange(0, config['monitor']['height'])
        self.field_width.setRange(0, config['monitor']['width'])
        self.field_height.setRange(0, config['monitor']['height'])
        self.field_left.valueChanged.connect(self.on_change_selection)
        self.field_top.valueChanged.connect(self.on_change_selection)
        self.field_width.valueChanged.connect(self.on_change_selection)
        self.field_height.valueChanged.connect(self.on_change_selection)
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
            screenshot.save(config['paths']['screenshot_background'])
        # Open a windoe with the background being the screenshot
        self.transparent_window = TransparentWindow()
        self.transparent_window.show()
        # Connect the signal from the DraggableBox for screenshot selection
        self.transparent_window.draggable_widget.signal_selection_change.connect(self.update_screenshot_selection)

    def on_save(self):
        try:
            with mss() as sct:
                screenshot = sct.grab({'left':self.transparent_window.draggable_widget.selection.left,
                                       'top':self.transparent_window.draggable_widget.selection.top,
                                       'width':self.transparent_window.draggable_widget.selection.width,
                                       'height':self.transparent_window.draggable_widget.selection.height})
                screenshot = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                screenshot.save(config['paths']['screenshot_selection'])
        except Exception as e:
            print(e)

    def on_close_screenshot(self):
        if self.transparent_window:
            self.transparent_window.close()
            self.transparent_window = None

    def on_change_selection(self):
        '''
        Pass changes to the screenshot selection from the ScreenshotApp to the DraggableBox
        '''
        try:
            selection = Box(int(self.field_left.text()),
                            int(self.field_top.text()),
                            int(self.field_width.text()),
                            int(self.field_height.text()))
            self.transparent_window.draggable_widget.on_change_selection(selection)
        except Exception as e:
            print(str(e))

    @pyqtSlot()
    def update_screenshot_selection(self):
        '''
        Handle the selection being changed from outside ScreenshotApp
        '''
        # Block signals to prevent triggering on_change_selection when programmatically updating values
        self.field_left.blockSignals(True)
        self.field_top.blockSignals(True)
        self.field_width.blockSignals(True)
        self.field_height.blockSignals(True)
        # Update the Position and Size fields
        selection = self.transparent_window.draggable_widget.selection
        self.field_left.setValue(selection.left)
        self.field_top.setValue(selection.top)
        self.field_width.setValue(selection.width)
        self.field_height.setValue(selection.height)
        # Unblock signals after the programmatic update
        self.field_left.blockSignals(False)
        self.field_top.blockSignals(False)
        self.field_width.blockSignals(False)
        self.field_height.blockSignals(False)

    def closeEvent(self, event):
        if self.transparent_window:
            self.transparent_window.close()
        event.accept()