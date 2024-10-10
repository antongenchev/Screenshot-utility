from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

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

        h_layout = QHBoxLayout()
        self.button_screenshot = QPushButton('Take a new screenshot', self)
        self.button_screenshot.clicked.connect(self.on_take_screenshot)
        self.button_close_screenshot = QPushButton('Close screenshot', self)
        self.button_close_screenshot.clicked.connect(self.on_close_screenshot)
        h_layout.addWidget(self.button_screenshot)
        h_layout.addWidget(self.button_close_screenshot)
        self.layout.addLayout(h_layout)

        self.setLayout(self.layout)

    def on_take_screenshot(self):
        print('Take screenshot')


    def on_close_screenshot(self):
        print('Close screenshot')