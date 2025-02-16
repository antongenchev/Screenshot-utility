# Configuration File Documentation (for config.json)

## Monitor
- **width**: (int) Width of the monitor in pixels.
- **height**: (int) Height of the monitor in pixels.

## Start Position
- **left**: (int) Distance from the left side of the monitor where the app gui starts.
- **top**: (int) Distance from the top of the monitor.
- **width**: (int) Initial width of the app gui.
- **height**: (int) Initial height of the app gui.

## Draggable Box
- **border**: (int) Thickness of the draggable box's border.
- **resize_border**: (int) Thickness of the border used for resizing the box.

## Paths
- **screenshot_background**: (string) Path to the background screenshot image.
- **screenshot_selection**: (string) Path to the screenshot selection image.

## Mementos
- **max_num_mementos**: (int) Maximum number of mementos (history or checkpoints) to keep.
- **time_limits**: (object) Contains timing restrictions for related mementos.
  - **MementoTransparentWindow**: (float) Maximum allowed time difference (in seconds) between two `MementoTransparentWindow` objects for them to be considered related. If two mementos are created by the `ScreenshotApp` within this time window, they are related.

## ZoomableLabel
- **min_pixels_per_side**: (int) Minimum number of pixels per side from the original cv2 image.
- **minimum_scale**: (float) Minimum scale allowed for zooming.

## Tools
Each tool has
- **name**: (str) The name of the tool e.g. "PencilTool".
- **order**: (int) The order in which the tools should be showed in the GUI.
- **options**: (optional[dict]) The tool specific options.
### PencilTool
- **pencil_colo**: (list) The default RGB color of the pencil e.g. [0, 255, 0] for green.
- **pencil_thickness**: (int) The default thickness of the pencil in pixels
- **pencil_opacity**: (float) The default opacity of the pencil between 0 and 1.
### TextTool
- **fonts**: (list) List of available font families.
- **font_name**: (str) The default font family from the fonts.
- **min_font_size**: (int) Minimum size of the text in pt.
- **max_font_size**: (int) Miximum size of the text in pt.
- **font_size**: (int) Default font size between min_font_size and max_font_size.
- **text_color**: (str) The default text color expressed in a hexidecimal string e.g. "#000000".
- **text_opacity**: (float) The default opacity in range between 0 and 1.
- **placeholder**: (str) The place holder text.
