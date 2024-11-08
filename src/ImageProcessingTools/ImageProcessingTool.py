import numpy as np
from src.DrawableElement import DrawableElement

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

    def create_drawable_element(self, instructions:dict={}, image:np.ndarray=None):
        '''
        Add a DrawableElement to the active layer

        Parameters:
            instructions: a dictionary with instructions which ImageProcessingTool.draw_drawable_element()
                can use to draw the drawable element
            image: image for the drawable element. If it is not provided it will be drawn by the tool
        '''
        img_height = self.image_processor.zoomable_label.img_height
        img_width = self.image_processor.zoomable_label.img_width
        drawable_element = DrawableElement(self.__class__.__name__,
                                           instructions,
                                           image=image,
                                           size=(img_height, img_width))
        self.image_processor.add_element(drawable_element)
        return drawable_element

    def draw_drawable_element(self, drawable_element:DrawableElement):
        raise NotImplementedError("This method should be overridden in subclasses.")