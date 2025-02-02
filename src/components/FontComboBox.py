from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QFont


class FontComboBox(QComboBox):
    def __init__(self, font_options, parent=None):
        super().__init__(parent)
        self.font_options = font_options

        # Hardcoded style parameters
        self.font_size = 16
        self.dropdown_height = 24
        self.dropdown_width = 200

        self.setFixedWidth(self.dropdown_width)

        self.populate_font_dropdown()

        # Connect selection change to update the current font in the combo box
        self.currentIndexChanged.connect(self.update_current_font)
        # Set the default font to the first font in the list (or a preset default)
        self.set_current_font(self.font_options[0])

    def populate_font_dropdown(self):
        """
        Populate the font dropdown with the fonts and their styles.
        Each item will display with its respective font style.
        """
        for font_name in self.font_options:
            font = QFont(font_name)
            font.setPointSize(self.font_size)
            item = font_name
            self.addItem(item)

            # Set the font for the item in the dropdown list
            font_item = self.model().itemFromIndex(self.model().index(self.count()-1, 0))
            font_item.setFont(font)

    def update_current_font(self):
        """
        Update the font of the selected item in the combo box.
        This makes sure the selected item shows the current font.
        """
        self.setFixedHeight(self.dropdown_height)

        selected_font_name = self.currentText()
        font = QFont(selected_font_name)
        font.setPointSize(self.font_size)
        self.setFont(font)

        # Update the display of the selected font name
        current_index = self.currentIndex()
        font_item = self.model().itemFromIndex(self.model().index(current_index, 0))
        font_item.setFont(font)

    def set_current_font(self, font_name):
        """
        Set the current font in the combo box.
        """
        index = self.findText(font_name)
        if index != -1:
            self.setCurrentIndex(index)
            self.update_current_font()