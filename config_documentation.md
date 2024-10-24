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
