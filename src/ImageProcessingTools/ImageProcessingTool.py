

class ImageProcessingTool:
    def __init__(self, image_processor):
        self.image_processor = image_processor
        self.drawing_enabled = False

    def create_ui(self):
        """Create the UI elements for this tool."""
        raise NotImplementedError("This method should be overridden in subclasses.")

    def on_mouse_press(self, x: int, y: int):
        """Called when the mouse is pressed."""
        raise NotImplementedError("This method should be overridden in subclasses.")

    def on_mouse_move(self, x: int, y: int):
        """Called when the mouse is moved."""
        raise NotImplementedError("This method should be overridden in subclasses.")

    def on_mouse_release(self, x: int, y: int):
        """Called when the mouse is released."""
        raise NotImplementedError("This method should be overridden in subclasses.")

    def set_tool(self):
        '''
        Set the current tool of the ImageProcessor to this ImageProcessing tool
        '''
        self.image_processor.set_tool(self)

    def enable(self):
        self.drawing_enabled = True
        self.image_processor.drawing_enabled = True
        self.image_processor.zoomable_label.drawing_enabled = True

    def disable(self):
        self.drawing_enabled = False
        self.image_processor.drawing_enabled = False
        self.image_processor.zoomable_label.drawing_enabled = False

    def is_enabled(self) -> bool:
        return self.drawing_enabled
