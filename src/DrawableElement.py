import numpy as np
import cv2
from typing import Tuple

class DrawableElement():
    def __init__(self,
                 tool_name:str,
                 instructions:dict={},
                 size:Tuple[int,int]=None):
        self.id = None # Unique id for the drawable element
        self.tool = tool_name # The tool which has created the drawable element
        self.z_index = None # The z-index of the element
        self.visible = None # bool
        self.instructions = instructions # The instructions used by the Tool to draw the element
        self.image = None # Image with the drawn element
        self.size = size # The size of the image. Tuple[int, int] (h,w)
        self.offset = (0, 0) # The offset to apply before adding self.image to the layer's image

    def clear_image(self):
        if self.size is None:
            raise ValueError("Image size is not set. Set `self.size` before calling `clear_image`.")
        height, width = self.size
        self.image = np.zeros((height, width, 4), dtype=np.uint8)
