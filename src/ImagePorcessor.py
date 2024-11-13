from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
import cv2
import numpy as np
from enum import IntEnum, auto
import importlib
import copy
from typing import List
from scipy.interpolate import CubicSpline
from src.ZoomableLabel import ZoomableLabel
from src.Layer import Layer, FakeLayer
from src.DrawableElement import DrawableElement
from src.config import config

from src.ImageProcessingToolSetting import ImageProcessingToolSetting
# Import ImageProcessingTools
from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from src.ImageProcessingTools.PencilTool import PencilTool

class ImageProcessor(QWidget):

    # The available image processing tools
    class tools(IntEnum):
        move = 0
        pencil = auto()

    def __init__(self,
                 zoomable_label:ZoomableLabel,
                 image_processing_tool_setting:ImageProcessingToolSetting):
        super().__init__()
        self.zoomable_label = zoomable_label
        self.current_tool = None
        self.tool_classes = {}
        self.layers:List[Layer] = [] # All the layers
        self.fake_layer:FakeLayer = None # layer for visualising stuff not part of what is drawn
        self.active_layer_index = 0 # the index of the active layer
        self.final_image = None # The final image after adding all the layers together

        self.image_processing_tool_setting = image_processing_tool_setting

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Load tools from the config.json file
        self.load_tools_from_config()

        for tool_name in sorted(self.tool_classes.keys(), key=lambda k: self.tool_classes[k]['order']):
            tool_obj = self.tool_classes[tool_name]['object']
            tool_widget = tool_obj.create_ui()
            layout.addWidget(tool_widget)

        self.setLayout(layout)

    def update_zoomable_label(self):
        '''
        Update the image shown in the zoomable label
        '''
        if self.fake_layer.visible:
            # If the fake layer is visible draw it on top
            final_image = self.overlay_images(self.final_image, self.fake_layer.final_image)
            self.zoomable_label.update_transformed_image(final_image)
        else:
            # If the fake layer is not visible display just the final image
            self.zoomable_label.update_transformed_image(self.final_image)

    ################
    # Handle tools #
    ################

    def load_tools_from_config(self):
        for tool in config['tools']:
            tool_name = tool["name"]
            module = importlib.import_module(f'src.ImageProcessingTools.{tool_name}')
            tool_class = getattr(module, tool_name)
            tool_obj = tool_class(self)
            self.tool_classes[tool_name] = {
                'class': tool_class,
                'object': tool_obj,
                'order': tool['order'],
            }

    def set_tool(self, tool: ImageProcessingTool):
        self.current_tool = tool

        settings_ui = self.current_tool.create_settings_ui()
        self.image_processing_tool_setting.set_tool_settings_ui(settings_ui)

    ##################
    # Handle signals #
    ##################

    def on_mouse_move(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel.

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        self.current_tool.on_mouse_move(x, y)

    def on_mouse_down(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel for left mouse button down event

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        self.current_tool.on_mouse_down(x, y)

    def on_mouse_up(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel for left mouse button release event

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        self.current_tool.on_mouse_up(x, y)

    def on_new_image(self):
        '''
        Handle signals from the ZoomableLable about a new image
        '''
        self.layers = [] # clear the previous layers
        image = copy.deepcopy(self.zoomable_label.original_image)
        # Add an alpha channel in case there isn't already one
        if image.shape[2] == 3:
            alpha_channel = np.full((image.shape[0], image.shape[1], 1), 255, dtype=np.uint8)
            image = np.concatenate((image, alpha_channel), axis=2)
        # Add a layer with the image and set the active layer index
        self.layers.append(Layer(self, image))
        self.active_layer_index = 0
        # Initialize the fake layer with a zeroed image)
        empty_image = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
        self.fake_layer = FakeLayer(self, image=empty_image)
        # Initialise the final image
        self.final_image = copy.deepcopy(image)

    #################
    # Layer methods #
    #################

    def add_layer(self, image=None):
        layer = Layer(image=image)
        self.layers.append(layer)
        self.active_layer_index = len(self.layers) - 1

    def remove_layer(self, index):
        if 0 <= index < len(self.layers):
            del self.layers[index]
            self.active_layer_index = min(self.active_layer_index, len(self.layers) - 1)

    def set_active_layer(self, index):
        if 0 <= index < len(self.layers):
            self.active_layer_index = index

    def toggle_layer_visibility(self, index):
        if 0 <= index < len(self.layers):
            self.layers[index].toggle_visibility()

    def render_layers(self):
        '''
        Render all layers
        '''
        self.zoomable_label.update_transformed_image()

    def render_layer(self, index:int) -> None:
        '''
        Render the layer with index `index`.
        That is update the final_image of the layer

        Parameters:
            index: the index of the layer in self.layers
        '''
        layer = self.layers[index]
        for drawable_element in layer.elements:
            self.render_element(drawable_element, redraw=False)
            # add element to layer

    def overlay_images(self, image_bottom:np.ndarray, image_top:np.ndarray) -> np.ndarray:
        '''
        Overlay two images and return the result

        Parameters:
            image_bottom: the image on the bottom. cv2 image with 4 channels
            image_top: the image on the top. cv2 image with 4 channels
        Returns:
            cv2 image with 4 channels. The result of placing image_top on top of image_bottom
        '''
        bottom_alpha = image_bottom[:, :, 3] / 255.0
        overlay_rgb = image_top[:, :, :3]
        overlay_alpha = image_top[:, :, 3] / 255.0
        image_result = np.zeros_like(image_bottom)
        for c in range(3): # Loop over the RGB channels
            image_result[:, :, c] = (overlay_rgb[:, :, c] * overlay_alpha +
                                   image_bottom[:, :, c] * (1 - overlay_alpha)).astype(np.uint8)
        # Compute the final alpha channel
        image_result[:, :, 3] = ((overlay_alpha + bottom_alpha * (1.0 - overlay_alpha)) * 255).astype(np.uint8)
        return image_result

    ###################
    # Element methods #
    ###################

    def render_element(self, drawable_element:DrawableElement, redraw:bool) -> None:
        if (not redraw) and drawable_element.image is not None:
            # Do not redraw if the image is already drawn
            return
        tool_name = drawable_element.tool
        tool_obj = self.tool_classes[tool_name]['object']
        tool_obj.draw_drawable_element(drawable_element)

    def add_element(self, drawable_element:DrawableElement):
        # Add the element to the current layer
        self.layers[self.active_layer_index].add_element(drawable_element)
        # Add the layers together to get the final image
        self.final_image = self.layers[self.active_layer_index].final_image # TODO implement multiple layers logic
        self.update_zoomable_label()

    def overlay_element_on_image(self, image:np.ndarray, drawable_element:DrawableElement):
        '''
        Modify an image by overlaying a drawable_element on top of it. Take into account opacity

        Parameters:
            image: an opencv image
            drawable_element: A drawable element that has already been rendered.
                If the drawable element has an affine transformation it will be applied when overlayig it
        '''
        if drawable_element.transformation is not None:
            # Apply the affine transformation if the drawable has such
            transformed_element_img = cv2.warpAffine(drawable_element.image,
                                                    drawable_element.transformation,
                                                    (image.shape[1], image.shape[0]))
            overlay_height, overlay_width = transformed_element_img.shape[:2]
            # Extract the offset (tx, ty) of the affine transformation matrix
            tx = int(drawable_element.transformation[0, 2])
            ty = int(drawable_element.transformation[1, 2])
            # Calculate the region of interest in the target image
            start_x = max(tx, 0)
            start_y = max(ty, 0)
            end_x = min(tx + overlay_width, image.shape[1])
            end_y = min(ty + overlay_height, image.shape[0])
            # Calculate ROI in the transformed image
            roi_transformed = transformed_element_img[start_y-ty:end_y-ty, start_x-tx:end_x-tx]
        else:
            # If no transformation, place the element at the origin
            roi_transformed = drawable_element.image
            start_x, start_y = 0, 0
            end_x, end_y = image.shape[1], image.shape[0]

        overlay_rgb = roi_transformed[:, :, :3] # RGB channels of the drawable element
        overlay_alpha = roi_transformed[:, :, 3] / 255.0 # The alpha channel of the drawable element
        # Invert the alpha channel for the background's contribution
        image_alpha = 1.0 - overlay_alpha
        # Define the corresponging region in the background image
        roi_image = image[start_y:end_y, start_x:end_x]
        # For each color channel, calculate the result by blending background and overlay
        for c in range(3): # Loop over the RGB channels
            roi_image[:, :, c] = (overlay_rgb[:, :, c] * overlay_alpha +
                                 roi_image[:, :, c] * image_alpha).astype(np.uint8)
        # Place the blended ROI back into the original image
        image[start_y:end_y, start_x:end_x] = roi_image

    def get_touch_element(self, x, y, r) -> DrawableElement:
        return self.layers[self.active_layer_index].get_touched_element(x, y, r)