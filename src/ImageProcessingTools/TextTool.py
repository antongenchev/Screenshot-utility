from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, \
    QSlider, QLabel, QColorDialog, QFrame, QGraphicsOpacityEffect
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QTextCursor, QTextBlockFormat, QTextCharFormat, QFont, QIcon, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from functools import partial
from src.utils.image_rendering import *
from src.components.FontComboBox import FontComboBox
from src.components.IconsComboBox import IconsComboBox
from typing import Optional, Tuple

class TextTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)
        self.font_options = self.config['options']['fonts']
        self.font_name = self.config['options']['font_name']
        self.font_size_min = self.config['options']['min_font_size']
        self.font_size_max = self.config['options']['max_font_size']
        self.real_font_size = self.config['options']['font_size']
        self.text_color = self.config['options']['text_color']
        self.text_opacity = self.config['options']['text_opacity']
        self.placeholder_text = self.config['options']['placeholder']
        self.alignment = 'Left'

        # State/instruction related members
        self.real_position: Tuple[int, int] = None # the position relative to the image
        self.resize_factor: float = None # the factor that adjusts the real font size based on the scale factor

        # Hardcoded values
        self.icon_button_width = 30
        self.icon_button_height = 30

        self.is_bold = False
        self.is_italic = False
        self.is_underline = False
        self.is_strikethrough = False

    def create_ui(self):
        """Create the button for the move tool."""
        self.button = QPushButton('Text')
        self.button.clicked.connect(partial(self.set_tool))
        return self.button

    def create_settings_ui(self):
        settings_widget = QWidget()
        layout = QHBoxLayout()

        # Font_options layout includes: font, font size, bold-italic-underline-strikethrough
        font_options_layout = QVBoxLayout()
        font_options_layout.setAlignment(Qt.AlignTop)
        font_options_layout.setSpacing(8)

        # Font Selection Dropdown
        font_dropdown = FontComboBox(self.font_options)
        # font_dropdown.addItems(self.font_options)
        font_dropdown.currentTextChanged.connect(self.set_font)
        font_options_layout.addWidget(font_dropdown)

        # Font Size Slider
        font_size_layout = QHBoxLayout()
        font_size_layout.setAlignment(Qt.AlignLeft)
        font_size_label_icon = QLabel()
        font_size_icon = QPixmap(f'{self.resources_path}/icon_font_size.svg').scaled(QSize(16, 16), aspectRatioMode=1)
        font_size_label_icon.setPixmap(font_size_icon)
        font_size_label_icon.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        font_size_label = QLabel()
        font_size_label.setText(f"({self.real_font_size})")
        font_size_label.setFixedWidth(40)
        # Create the font size slider
        font_size_slider = QSlider(Qt.Horizontal)
        font_size_slider.setMinimum(self.font_size_min)
        font_size_slider.setMaximum(self.font_size_max)
        font_size_slider.setValue(self.real_font_size)
        font_size_slider.valueChanged.connect(self.set_font_size)
        font_size_slider.valueChanged.connect(lambda value: self.update_font_size_label(value, font_size_label))
        # Add the labels with icon and text to the layout
        font_size_layout.addWidget(font_size_label_icon)
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(font_size_slider)
        font_options_layout.addLayout(font_size_layout)

        # Add icon buttons for Bold, Italic, and Underline in a horizontal layout
        icon_layout = QHBoxLayout()
        icon_layout.setSpacing(2)
        icon_layout.setAlignment(Qt.AlignLeft) 

        # Bold button
        self.bold_button = QPushButton()
        self.bold_button.setIcon(self.create_svg_icon(f'{self.resources_path}/icon_bold.svg'))
        self.bold_button.setIconSize(QSize(24, 24))
        self.bold_button.setFixedSize(QSize(self.icon_button_width, self.icon_button_height))
        self.bold_button.clicked.connect(self.toggle_bold)
        icon_layout.addWidget(self.bold_button)

        # Italic button
        self.italic_button = QPushButton()
        self.italic_button.setIcon(self.create_svg_icon(f'{self.resources_path}/icon_italic.svg'))
        self.italic_button.setIconSize(QSize(24, 24))
        self.italic_button.setFixedSize(QSize(self.icon_button_width, self.icon_button_height))
        self.italic_button.clicked.connect(self.toggle_italic)
        icon_layout.addWidget(self.italic_button)

        # Underline button
        self.underline_button = QPushButton()
        self.underline_button.setIcon(self.create_svg_icon(f'{self.resources_path}/icon_underline.svg'))
        self.underline_button.setIconSize(QSize(24, 24))
        self.underline_button.setFixedSize(QSize(self.icon_button_width, self.icon_button_height))
        self.underline_button.clicked.connect(self.toggle_underline)
        icon_layout.addWidget(self.underline_button)

        # Strikethrough button
        self.strikethrough_button = QPushButton()
        self.strikethrough_button.setIcon(self.create_svg_icon(f'{self.resources_path}/icon_strikethrough.svg'))
        self.strikethrough_button.setIconSize(QSize(24, 24))
        self.strikethrough_button.setFixedSize(QSize(self.icon_button_width, self.icon_button_height))
        self.strikethrough_button.clicked.connect(self.toggle_strikethrough)
        icon_layout.addWidget(self.strikethrough_button)

        # Add the icons to the font_options_layout
        font_options_layout.addLayout(icon_layout)
        layout.addLayout(font_options_layout)
        # Add a vertical line
        vertical_line = QFrame()
        vertical_line.setFrameShape(QFrame.VLine)
        vertical_line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(vertical_line)

        # Color and opacity layout
        color_layout = QVBoxLayout()
        color_layout.setAlignment(Qt.AlignTop)

        # Text Color Picker Button + text representatio + color shown
        color_choice_layout = QHBoxLayout()
        color_choice_layout.setAlignment(Qt.AlignLeft)
        text_color_button = QPushButton()
        text_color_button.setIcon(self.create_svg_icon(f'{self.resources_path}/icon_color_choice.svg'))
        text_color_button.setIconSize(QSize(24, 24))
        text_color_button.setFixedSize(QSize(40, 40))
        text_color_button.clicked.connect(self.open_color_picker)
        color_choice_layout.addWidget(text_color_button)
        self.color_hex_label = QLabel(f"{self.text_color}")
        self.color_hex_label.setFixedWidth(50)
        monospace_font = QFont("Courier New")
        monospace_font.setStyleHint(QFont.Monospace)
        self.color_hex_label.setFont(monospace_font)
        color_choice_layout.addWidget(self.color_hex_label)
        self.color_display_label = QLabel()
        self.color_display_label.setFixedSize(20, 20)  # Width and height of the rectangle
        self.color_display_label.setStyleSheet(f"background-color: {self.text_color}; border: 1px solid black;")
        color_choice_layout.addWidget(self.color_display_label)

        # Color Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.setAlignment(Qt.AlignLeft)
        opacity_label_icon = QLabel()
        opacity_icon = QPixmap(f'{self.resources_path}/icon_opacity.svg').scaled(QSize(16, 16), aspectRatioMode=1)
        opacity_label_icon.setPixmap(opacity_icon)
        opacity_label_icon.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.opacity_label = QLabel(f"({int(self.text_opacity * 100)}%)")
        self.opacity_label.setFixedWidth(40)
        # Create the opacity slider
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setMinimum(0)
        opacity_slider.setMaximum(100)
        opacity_slider.setValue(int(self.text_opacity * 100))
        opacity_slider.valueChanged.connect(self.set_text_opacity)
        # Add the labels with icon and text to the layout
        opacity_layout.addWidget(opacity_label_icon)
        opacity_layout.addWidget(self.opacity_label)
        opacity_layout.addWidget(opacity_slider)

        color_layout.addLayout(color_choice_layout)
        color_layout.addLayout(opacity_layout)
        layout.addLayout(color_layout)
        # Add a vertical line
        vertical_line = QFrame()
        vertical_line.setFrameShape(QFrame.VLine)
        vertical_line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(vertical_line)

        # Text Alignment Dropdown
        others_layout = QVBoxLayout()
        others_layout.setAlignment(Qt.AlignTop)

        alignment_dropdown = IconsComboBox()
        alignment_dropdown.addItems(["Left", "Center", "Right"],
                                    [f'{self.resources_path}/icon_alignment_{x}.svg' for x in ['left', 'center', 'right']])
        alignment_dropdown.setFixedWidth(90)
        alignment_dropdown.currentTextChanged.connect(self.set_alignment)
        others_layout.addWidget(alignment_dropdown)
        layout.addLayout(others_layout)

        settings_widget.setLayout(layout)
        return settings_widget

    def on_mouse_down(self, x: int, y: int):
        '''
        Handle mouse down events. Create a widget for writing text. Mouse events
        from existing text_widgets will not reach this function.

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        # Save and delete previous text_widget if it exists
        self.save_text_widget()
        self.remove_previous_text_widget()
        # Create new text_widget.
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
        if old_text_widget := self.get_text_widget():
            old_text_widget = self.image_processor.zoomable_widget.overlay.text_field
            old_text_widget.setParent(None)
            old_text_widget.deleteLater()
            self.image_processor.zoomable_widget.overlay.text_field = None

    def save_text_widget(self) -> None:
        '''
        Saves the current text_widget if it contains text.
        '''
        if (text_widget := self.get_text_widget()) and text_widget.toPlainText():
            # Get original font size
            font = text_widget.font()
            font.setPointSize(int(self.real_font_size)) # Set font size
            text_widget.setFont(font)
            self.resize_text_widget(text_widget)

            # Deselect any selected text
            cursor = text_widget.textCursor()
            cursor.clearSelection()
            text_widget.setTextCursor(cursor)
            text_widget.repaint()

            # Render widget onto a pixmap
            pixmap = QPixmap(text_widget.size())
            pixmap.fill(Qt.transparent)
            text_widget.render(pixmap)

            # Convert QPixmap to cv2 image
            cv_image = qpixmap_to_cv2(pixmap)

            text_data = text_widget.toHtml()
            position = text_widget.pos()
            size = text_widget.size()

            # Get opacity
            opacity_effect = text_widget.graphicsEffect()
            opacity = opacity_effect.opacity() if opacity_effect else 1.0

            instructions = {
                'html': text_data,
                'x': position.x(),
                'y': position.y(),
                'width': size.width(),
                'height': size.height(),
                'opacity': opacity
            }

            # Create the new drawable element
            instructions = {}
            transformation = np.array([[1, 0, self.real_position[0]], [0, 1, self.real_position[1]]], dtype=np.float32) # The affine transformation with offset
            self.create_drawable_element(instructions,
                                         cv_image,
                                         touch_mask=255 * np.ones(cv_image.shape[:2]),
                                         transformation=transformation)

    def create_new_text_widget(self, x:int, y:int) -> None:
        '''
        Create a new text widget in the overlay with location corresponding to the
        coordinates x,y.

        Parameters:
            x - the x-coordinate in the image
            y - the y-coordinate in the image
        '''
        # Offset so vertically we start typing from the middle of the line
        y = y - int(self.real_font_size * (2/3)) # 4 pixels is 1pt
        self.real_position = (x, y) # position relative to the image

        # Create a text field in the overlay of the zoomable widget
        text_widget = QTextEdit(self.image_processor.zoomable_widget.overlay)
        text_widget.setPlaceholderText(self.placeholder_text)
        self.image_processor.zoomable_widget.overlay.text_field = text_widget

        # Move the the text_widget to the correct coordinates
        shown_x, shown_y = self.image_processor.zoomable_label.convert_image_coordinates_to_shown(x, y)
        text_widget.move(int(shown_x), int(shown_y))

        # Set the initial styling
        self.get_resize_factor()
        font = text_widget.font()
        font.setPointSize(int(self.real_font_size * self.resize_factor)) # Set font size
        if self.font_name:
            font.setFamily(self.font_name) # Set font name if available
        text_widget.setFont(font)
        if self.text_color:
            text_widget.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                border: none;
                color: {hex_to_rgba(self.text_color, self.text_opacity)};
            }}
        """)

        # Set the opacity
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(self.text_opacity)
        text_widget.setGraphicsEffect(opacity_effect)

        # Set the initial size based on the placeholder text so it fits on one line
        self.resize_text_widget(text_widget)
        self.set_alignment(self.alignment)

        text_widget.setWordWrapMode(True)
        text_widget.textChanged.connect(lambda: self.resize_text_widget(text_widget))

        text_widget.setFocus()
        text_widget.show()

        # Set bold, italic, underline additional styling
        if self.is_bold:
            cursor = text_widget.textCursor()
            format = QTextCharFormat()
            format.setFontWeight(QFont.Bold if not cursor.charFormat().font().weight() == QFont.Bold else QFont.Normal)
            cursor.mergeCharFormat(format)
            text_widget.setTextCursor(cursor)
        if self.is_italic:
            cursor = text_widget.textCursor()
            format = QTextCharFormat()
            format.setFontItalic(not cursor.charFormat().font().italic())
            cursor.mergeCharFormat(format)
            text_widget.setTextCursor(cursor)
        if self.is_underline:
            cursor = text_widget.textCursor()
            format = QTextCharFormat()
            format.setFontUnderline(not cursor.charFormat().font().underline())
            cursor.mergeCharFormat(format)
            text_widget.setTextCursor(cursor)
        if self.is_strikethrough:
            cursor = text_widget.textCursor()
            format = QTextCharFormat()
            format.setFontStrikeOut(self.is_strikethrough)
            cursor.mergeCharFormat(format)
            text_widget.setTextCursor(cursor)

    def resize_text_widget(self, text_widget):
        '''
        Resize the QTextEdit dynamically to fit its content.

        Parameters:
            text_widget - The QTextEdit widget to resize
        '''
        # Get the document's layout and compute the full content size
        document = text_widget.document()
        document_layout = document.documentLayout()

        # Determine text content size or use placeholder text to calculate size if empty
        if not document.toPlainText().strip():
            placeholder_text = text_widget.placeholderText()
            font_metrics = text_widget.fontMetrics()
            text_width = font_metrics.horizontalAdvance(placeholder_text)  # Width of the placeholder text
            text_height = font_metrics.height()  # Height of one line of text
        else:
            # Calculate content size based on actual text
            text_width = document.idealWidth()
            text_height = document_layout.documentSize().height()

        # Account for padding/margins of the text widget
        margins = text_widget.contentsMargins()
        additional_padding = 10
        line_spacing = text_widget.fontMetrics().lineSpacing()
        total_width = int(text_width + margins.left() + margins.right()) + additional_padding
        total_height = int(text_height + margins.top() + margins.bottom()) + additional_padding + line_spacing

        # Ensure no scrollbars by setting the exact dimensions of the content
        text_widget.setFixedSize(total_width, total_height)

    def set_font(self, font_name:str):
        '''
        Set the font family for the text widget.
        '''
        self.font_name = font_name
        if current_widget := self.get_text_widget():
            current_font = current_widget.font()
            current_font.setFamily(font_name)
            current_widget.setFont(current_font)
            self.resize_text_widget(current_widget)
            current_widget.setFocus()

    def set_font_size(self, size):
        '''
        Set the font size for the textwidget.
        '''
        self.real_font_size = size
        if current_widget := self.get_text_widget():
            current_font = current_widget.font()
            current_font.setPointSize(int(size * self.resize_factor))
            current_widget.setFont(current_font)
            self.resize_text_widget(current_widget)
            current_widget.setFocus()

    def update_font_size_label(self, value: int, label: QLabel):
        '''
        Update the font size label dynamically when the slider value changes.

        Parameters:
            value - The current value of the slider
            label - The QLabel to update
        '''
        label.setText(f"({value})")

    def toggle_bold(self):
        # Toggle bold state
        self.is_bold = not self.is_bold
        self.highlight_button('bold_button', self.is_bold)
        if current_widget := self.get_text_widget():
            cursor = current_widget.textCursor()
            format = QTextCharFormat()
            format.setFontWeight(QFont.Bold if not cursor.charFormat().font().weight() == QFont.Bold else QFont.Normal)
            cursor.mergeCharFormat(format)
            current_widget.setTextCursor(cursor)
            current_widget.setFocus()

    def toggle_italic(self):
        # Toggle italic state
        self.is_italic = not self.is_italic
        self.highlight_button('italic_button', self.is_italic)
        if current_widget := self.get_text_widget():
            cursor = current_widget.textCursor()
            format = QTextCharFormat()
            format.setFontItalic(not cursor.charFormat().font().italic())
            cursor.mergeCharFormat(format)
            current_widget.setTextCursor(cursor)
            current_widget.setFocus()

    def toggle_underline(self):
        # Toggle underline state
        self.is_underline = not self.is_underline
        self.highlight_button('underline_button', self.is_underline)
        if current_widget := self.get_text_widget():
            cursor = current_widget.textCursor()
            format = QTextCharFormat()
            format.setFontUnderline(not cursor.charFormat().font().underline())
            cursor.mergeCharFormat(format)
            current_widget.setTextCursor(cursor)
            current_widget.setFocus()

    def toggle_strikethrough(self):
        # Toggel strikethroguh state
        self.is_strikethrough = not self.is_strikethrough
        self.highlight_button('strikethrough_button', self.is_strikethrough)
        if current_widget := self.get_text_widget():
            cursor = current_widget.textCursor()
            format = QTextCharFormat()
            format.setFontStrikeOut(self.is_strikethrough)
            cursor.mergeCharFormat(format)
            current_widget.setTextCursor(cursor)
            current_widget.setFocus()

    def open_color_picker(self):
        '''
        Open a QColorDialog to select a color for the text widget.
        '''
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color.name()
            if current_widget := self.get_text_widget():
                current_widget.setStyleSheet(f"""
                    QTextEdit {{
                        background: transparent;
                        border: none;
                        color: {hex_to_rgba(self.text_color, self.text_opacity)};
                    }}
                """)
                current_widget.setFocus()
            # Update the label
            self.color_hex_label.setText(f"{color.name()}")
            # Update the rectangle showing the current color
            self.color_display_label.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")

    def set_text_opacity(self, value:int):
        self.text_opacity = value / 100
        self.opacity_label.setText(f'({value}%)')

        if current_widget := self.get_text_widget():
            current_widget.setStyleSheet(f"""
                QTextEdit {{
                    background: transparent;
                    border: none;
                    color: {hex_to_rgba(self.text_color, self.text_opacity)};
                }}
            """)
            current_widget.setFocus()

    def set_alignment(self, alignment:str) -> None:
        '''
        Set the alignment for the text widget.
        '''
        self.alignment = alignment
        if current_widget := self.get_text_widget():
            document = current_widget.document()
            cursor = QTextCursor(document)

            # Create a QTextBlockFormat and set the alignment
            block_format = QTextBlockFormat()

            if alignment == "Left":
                block_format.setAlignment(Qt.AlignLeft)
            elif alignment == "Center":
                block_format.setAlignment(Qt.AlignCenter)
            elif alignment == "Right":
                block_format.setAlignment(Qt.AlignRight)

            # Apply the block format to the entire document
            cursor.select(QTextCursor.Document)
            cursor.mergeBlockFormat(block_format)
            cursor.clearSelection()
            # Update the text widget with the new alignment
            current_widget.setTextCursor(cursor)
            current_widget.setFocus()

    def get_resize_factor(self) -> float:
        '''
        Calculate the resize factor needed to adjust the font size based on the zoom lavel of the zoomable label.

        Returns:
            float: The resize_factor such that self.resize_factor * self.real_font_size = shown_font_size
        '''
        self.resize_factor = self.image_processor.zoomable_label.scale_factor
        return self.resize_factor

    def text_widget_exists(self) -> bool:
        '''
        Check if there is a text widget in the overlay
        '''
        return hasattr(self.image_processor.zoomable_widget.overlay, 'text_field') \
            and self.image_processor.zoomable_widget.overlay.text_field

    def get_text_widget(self) -> Optional[QTextEdit]:
        '''
        Get the text_widget from the overlay if such a widget exists

        Returns:
            Optional[QTextEdit]: The QTextEdit object if it exists otherwise a None
        '''
        if hasattr(self.image_processor.zoomable_widget.overlay, 'text_field') \
        and (text_widget := self.image_processor.zoomable_widget.overlay.text_field):
            return text_widget

    def create_svg_icon(self, icon_path):
        '''
        Helper function to create QIcon from SVG file path
        '''
        icon = QIcon()
        renderer = QSvgRenderer(icon_path)
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        icon.addPixmap(pixmap)
        return icon

    def highlight_button(self, button_name, active):
        '''
        Highlight the button when it is toggled.
        '''
        button = getattr(self, button_name, None)
        if button:
            if active:
                button.setStyleSheet("background-color: lightgray; border-radius: 5px;")
            else:
                button.setStyleSheet("")


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """
    Convert a hexadecimal color to an RGBA string.

    Paramters:
        hex_color: The hexadecimal color string (e.g., #ffffff).
        alpha: A float between 0.0 (fully transparent) and 1.0 (fully opaque).

    Returns:
        A string in the format 'rgba(r, g, b, a)'.
    """
    hex_color = hex_color.lstrip('#')  # Remove the '#' symbol
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    a = int(alpha * 255)  # Convert alpha (0.0-1.0) to 0-255
    return f"rgba({r}, {g}, {b}, {a})"
