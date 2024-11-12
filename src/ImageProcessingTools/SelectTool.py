from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton, QWidget
from functools import partial

class SelectTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)

    def create_ui(self):
        """Create the button for the move tool."""
        self.button = QPushButton('Select')
        self.button.clicked.connect(partial(self.set_tool))
        return self.button

    def create_settings_ui(self):
        return QWidget()

    def set_tool(self):
        super().set_tool()
        self.disable()