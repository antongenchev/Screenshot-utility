from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton
from functools import partial

class MoveTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)

    def create_ui(self):
        """Create the button for the move tool."""
        self.button = QPushButton('Move')
        self.button.clicked.connect(partial(self.set_tool))
        return self.button
    
    def set_tool(self):
        self.disable()