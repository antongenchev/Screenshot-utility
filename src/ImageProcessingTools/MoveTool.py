from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtCore import QSize
from src.utils.image_rendering import create_svg_icon
from functools import partial

class MoveTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)

    def create_ui(self):
        """Create the button for the move tool."""
        self.button = QPushButton()
        self.button.setIcon(create_svg_icon(f'{self.resources_path}/tool_button.svg'))
        self.button.setIconSize(QSize(36, 36))
        self.button.setFixedSize(QSize(36, 36))
        self.button.clicked.connect(partial(self.set_tool))

        # Use to keep the button highlighted because after enable there is an immediate
        # disable for this tool.
        self.should_be_highlithed = False

        return self.button

    def create_settings_ui(self):
        return QWidget()

    def set_tool(self):
        super().set_tool()
        self.disable()

    def enable(self):
        self.button.setStyleSheet("background-color: lightgray; border-radius: 5px;")
        self.should_be_highlithed = True
        return super().enable()

    def disable(self):
        result = super().disable()

        # Make sure the button of the MoveTool is highligthed when this is the current tool
        if not self.should_be_highlithed:
            self.button.setStyleSheet("")
        self.should_be_highlithed = False

        return result