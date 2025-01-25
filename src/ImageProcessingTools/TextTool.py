from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton, QWidget, QLineEdit, QTextEdit
from PyQt5.QtCore import QSize
from functools import partial

class TextTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)

    def create_ui(self):
        """Create the button for the move tool."""
        self.button = QPushButton('Text')
        self.button.clicked.connect(partial(self.set_tool))
        return self.button

    def create_settings_ui(self):
        return QWidget()

    def on_mouse_down(self, x: int, y: int):
        '''
        Handle mouse down events. Create a widget for writing text

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        self.remove_previous_text_widget()
        self.create_new_text_widget(x, y)

    def on_mouse_up(self, x: int, y: int):
        pass

    def on_mouse_move(self, x: int, y: int):
        pass

    def remove_previous_text_widget(self) -> None:
        '''
        Remove an already existing overlay.text_field if such one already exists.
        If the existing text_field/text_widget has text written into it then save
        the text in a drawable element and draw the drawable element.
        '''
        # Check if a previous text widget exists, and remove it if necessary
        if hasattr(self.image_processor.zoomable_widget.overlay, 'text_field') \
        and self.image_processor.zoomable_widget.overlay.text_field is not None:
            old_text_widget = self.image_processor.zoomable_widget.overlay.text_field
            old_text_widget.setParent(None)
            old_text_widget.deleteLater()
            self.image_processor.zoomable_widget.overlay.text_field = None

    def create_new_text_widget(self, x:int, y:int) -> None:
        '''
        Create a new text widget in the overlay with location corresponding to the
        coordinates x,y.

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        # Create a text field in the overlay of the zoomable widget
        text_widget = QTextEdit(self.image_processor.zoomable_widget.overlay)
        text_widget.setPlaceholderText("enter")
        self.image_processor.zoomable_widget.overlay.text_field = text_widget

        # Move the the text_widget to the correct coordinates
        shown_x, shown_y = self.image_processor.zoomable_label.convert_image_coordinates_to_shown(x, y)
        text_widget.move(int(shown_x), int(shown_y))

        text_widget.setWordWrapMode(True)
        text_widget.textChanged.connect(lambda: self.resize_text_widget(text_widget))

        # Set styling
        text_widget.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: black; /* Adjust the text color as needed */
                font-size: 14px; /* Adjust the font size */
            }""")

        text_widget.setFocus()
        text_widget.show()

    def resize_text_widget(self, text_widget):
        '''
        Resize the QTextEdit dynamically to fit its content.

        Parameters:
            text_widget - The QTextEdit widget to resize
        '''
        document = text_widget.document()
        document_size = document.size()
        text_widget.setFixedSize(QSize(int(document_size.width()) + 10, int(document_size.height()) + 10))