
class DrawableElement():
    def __init__(self, tool_name:str, instructions:dict={}):
        self.id = None # Unique id for the drawable element
        self.tool = tool_name # The tool which has created the drawable element
        self.z_index = None # The z-index of the element
        self.instructions = instructions # The instructions used by the Tool to draw the element
        self.image = None # Image with the drawn element