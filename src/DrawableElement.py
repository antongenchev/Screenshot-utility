import numpy as np
import cv2
from typing import Tuple

class DrawableElement():
    def __init__(self,
                 tool_name:str,
                 instructions:dict={},
                 image:np.ndarray=None,
                 size:Tuple[int,int]=None,
                 touch_mask:np.ndarray=None):
        self.id = None # Unique id for the drawable element
        self.tool = tool_name # The tool which has created the drawable element
        self.z_index = None # The z-index of the element
        self.visible = None # bool
        self.instructions = instructions # The instructions used by the Tool to draw the element
        self.image = image # Image with the drawn element
        self.touch_mask = touch_mask # cv2 image with 1 channel with the same size as self.image
        self.size = size # The size of the image. Tuple[int, int] (h,w)
        self.offset = (0, 0) # The offset to apply before adding self.image to the layer's image

    def clear_image(self):
        if self.size is None:
            raise ValueError("Image size is not set. Set `self.size` before calling `clear_image`.")
        height, width = self.size
        self.image = np.zeros((height, width, 4), dtype=np.uint8)
        self.touch_mask = np.zeros((height, width), dtype=np.uint8)

    def is_touched(self, x:int, y:int, r:int) -> bool:
        '''
        Check if a given coordinate is on top of the drawable element

        Parameters:
            x - the x coordinate
            y - the y coordinate
            r - the radius around (x, y
        Returns:
            bool: True if the element is touched, False otherwise
        '''
        # Cannot check for a touch if the element has no touchmask
        if self.touch_mask:
            return False

        # Translate global coordinates (x, y) to local coordinates within the touch_mask      
        local_x = x - self.offset[0]
        local_y = y - self.offset[0]

        # Check bounds to prevent out-of-range access
        if (local_x < 0 or local_y < 0 or
            local_x >= self.touch_mask.shape[1] or
            local_y >= self.touch_mask.shape[0]):
            return False

        # Define the bounding box for the radius around (local_x, local_y)
        x_min = max(local_x - r, 0)
        x_max = min(local_x + r, self.touch_mask.shape[1] - 1)
        y_min = max(local_y - r, 0)
        y_max = min(local_y + r, self.touch_mask.shape[0] - 1)

        # Check the area within the radius for any pixel with a value of 255
        for i in range(y_min, y_max + 1):
            for j in range(x_min, x_max + 1):
                # Check if (i, j) is within radius `r` from (local_x, local_y)
                if (i - local_y)**2 + (j - local_x)**2 <= r**2:
                    if self.touch_mask[i, j] == 255:
                        return True # Touched area found
        return False