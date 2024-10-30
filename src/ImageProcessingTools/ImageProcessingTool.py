

class ImageProcessingTool:
    def __init__(self, image_processor):
        self.image_processor = image_processor
        self.drawing_enabled = False

        self.config = {}
        self.load_config()

    def create_ui(self):
        """Create the UI elements for this tool."""
        raise NotImplementedError("This method should be overridden in subclasses.")

    def on_mouse_down(self, x: int, y: int):
        """Called when the mouse is pressed."""
        raise NotImplementedError("This method should be overridden in subclasses.")

    def on_mouse_move(self, x: int, y: int):
        """Called when the mouse is moved."""
        raise NotImplementedError("This method should be overridden in subclasses.")

    def on_mouse_up(self, x: int, y: int):
        """Called when the mouse is released."""
        raise NotImplementedError("This method should be overridden in subclasses.")

    def set_tool(self):
        '''
        Set the current tool of the ImageProcessor to this ImageProcessing tool
        '''
        self.image_processor.set_tool(self)
        self.enable()

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

    def load_config(self):
        '''
        Get the config for the this tool. That is:
        self.config = config['tools']['<current tool>']
        '''
        from src.config import config
        config_tools = config['tools']
        for config_tool in config_tools:
            if self.__class__.__name__ == config_tool['name']:
                self.config = config_tool
                break