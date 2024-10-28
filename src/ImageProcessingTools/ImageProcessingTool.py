

class ImageProcessingTool:
    def __init__(self, image_processor):
        pass

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
