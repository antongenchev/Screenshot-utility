import cv2
import numpy as np
from typing import List, Union
import copy
from src.DrawableElement import DrawableElement

class Layer:
    def __init__(self, image_processor, image=None, visible=True):
        self.image_processor = image_processor
        self.image = image # The starting image on which we draw
        self.final_image = copy.deepcopy(image)
        self.visible = visible # Is the layer visible
        self.drawing_enabled = False
        self.elements:List[DrawableElement] = []

    def toggle_visibility(self):
        self.visible = not self.visible

    def add_element(self, element:DrawableElement):
        '''
        Add a new element to the layer. Put it at the top of the layer.
        Update the final image of the layer

        Parameters:
            element: the drawable element to be added
        '''
        self.elements.append(element) # add the drawable element
        self.image_processor.render_element(element, redraw=False) # render the drawable element
        self.image_processor.overlay_element_on_image(self.final_image, element)

    def remove_element(self, index:int) -> None:
        if 0 <= index < len(self.elements):
            del self.elements[index]

    def get_elements(self:DrawableElement) -> List[DrawableElement]:
        return self.elements

    def get_element_index(self, element:DrawableElement) -> Union[int, None]:
        '''
        Given a drawable element return the index of the element in the list of element

        Parameters:
            element - the drawable element
        Retruns: the index of the drawable element
        '''
        for i in range(len(self.elements)):
            if element is self.elements[i]:
                return i

    #############
    # Rendering #
    #############

    def render_layer_hard(self) -> None:
        '''
        Rerender the whole layer by rerendering every element and adding it.
        This method renders the layer from instructions without using any intermediate results/images to speed up
        Note that the starting image (self.image) might already contain some drawable elements which are no longer
        kept as elements but are drawn straight on the image
        '''
        # Reset the final image
        self.final_image = copy.deepcopy(self.image)
        for element in self.elements:
            # Rerender every element
            self.image_processor.render_element(element, redraw=True)
            # Add the elements to the layer
            self.image_processor.overlay_element_on_image(self.final_image, element)

    def rerender_after_element_update(self, drawable_element:DrawableElement, redraw:bool=False) -> None:
        '''
        Rerenders the layer after a single element has been updated. The element will not be redrawn.

        Parameters:
            drawable_element - the drawable element to redraw. Must be from the list self.elements
            redraw - whether to redraw the drawable element from instructions
        '''
        # Find the index of the updated drawable element
        element_index = self.get_element_index(drawable_element)

        # Render everything below the chosen drawable element
        image_below = self.render_partial_layer(0, end_index=element_index)


        # Render everything above the chosen drawable element
        image_above = self.render_partial_layer(start_index=element_index, end_index=len(self.elements))

        # Combine image_below, the drawable element, and image_above to get the final image
        self.final_image = copy.deepcopy(self.image)
        self.final_image = self.image_processor.overlay_images(self.final_image, image_below)
        self.image_processor.overlay_element_on_image(self.final_image, drawable_element)
        self.final_image = self.image_processor.overlay_images(self.final_image, image_above)

    def render_partial_layer(self, start_index:int, end_index:int) -> np.ndarray:
        '''
        Render part of the layer. Add the drawable elements together

        Parameters:
            start_index - the index of the first drawable element to draw
            end_index - the index of the last drawable element to draw
        '''
        # Create a new image on which we will draw
        image = np.zeros_like(self.image)
        # Draw the drawable elements on top of the image
        for i in range(start_index, end_index):
            self.image_processor.overlay_element_on_image(image, self.elements[i])
        return image

    def get_touched_element(self, x:int, y:int, r:int) -> DrawableElement:
        '''
        Parameters:
            x - the x coordinate
            y - the y coordinate
            r - the radius around (x, y)
        Returns:
            DrawablElement: return the topmost drawable element that was clicked.
                If there is no such element return None
        '''
        for element in reversed(self.elements):
            if element.is_touched(x, y, r):
                return element

class FakeLayer(Layer):
    def __init__(self, image_processor, image=None, visible=True):
        super().__init__(image_processor, image, visible)

    def clear_final_image(self) -> None:
        '''
        Clears just the final_image of the layer. This is used when we have drawn
        directly to the final_image without modifying the actual contents of the layer
        '''
        self.final_image = np.zeros_like(self.final_image)

