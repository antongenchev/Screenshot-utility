from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton

class PencilTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)

    def create_ui(self):
        """Create the button for the pencil tool."""
        self.button = QPushButton('Draw')
        self.button.setCheckable(True)
        self.button.clicked.connect(self.toggle_drawing)
        return self.button

    def on_mouse_press(self, x: int, y: int):
        pass

    def on_mouse_move(self, x: int, y: int):
        pass

    def on_mouse_release(self, x: int, y: int):
        pass

    def toggle_drawing(self):
        if self.drawing_enabled:
            self.disable()
            self.button.setChecked(False)
        else:
            self.enable()
            self.button.setChecked(True)