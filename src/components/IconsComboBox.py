from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QIcon


class IconsComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def addItems(self, choice_names, icon_paths=None):
        """
        Adds icon options to the combo box. Takes alignment names and optionally icon paths.
        
        Parameters:
            choice_names (list): List of alignment names like ["Left", "Center", "Right"]
            icon_paths (list, optional): List of icon paths corresponding to each alignment option.
        """
        if icon_paths is None:
            icon_paths = [""] * len(choice_names)  # Default to empty if no icons provided

        for alignment_name, icon_path in zip(choice_names, icon_paths):
            self.add_item_with_icon(alignment_name, icon_path)
    
    def add_item_with_icon(self, choice_name, icon_path):
        """
        Adds an item to the combo box with an associated icon.
        
        Parameters:
            choice_name (str): The alignment name (e.g., "Left", "Center", "Right")
            icon_path (str): The file path to the icon image (e.g., "left-align-icon.png")
        """
        if icon_path:
            icon = QIcon(icon_path)
            self.addItem(icon, choice_name)
        else:
            self.addItem(choice_name)  # Add just the text if no icon provided
