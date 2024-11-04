
class DrawableElement():
    def __init__(self):
        self.id = None # Unique id for the drawable element
        self.tool = None # The tool which has created the drawable element
        self.z_index = None # The z-index of the element
        self.instructions = {} # The instructions used by the Tool to draw the element
        self.image = None # Image with the drawn element