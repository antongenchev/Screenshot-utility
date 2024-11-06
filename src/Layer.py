import cv2
from src.DrawableElement import DrawableElement

class Layer:
    def __init__(self, image_processor, image=None, visible=True):
        self.image_processor = image_processor
        self.image = image # The starting image on which we draw
        self.final_image = image
        self.visible = visible # Is the layer visible
        self.drawing_enabled = False
        self.elements = []

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

    def remove_element(self, index):
        if 0 <= index < len(self.elements):
            del self.elements[index]

    def get_elements(self:DrawableElement):
        return self.elements

    def render_layer(self, layer):
        '''
        Update self.image
        '''
        pass