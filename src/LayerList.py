from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PyQt5.QtCore import Qt

class LayerListWidget(QWidget):
    def __init__(self, image_processor):
        super().__init__()
        self.image_processor = image_processor

        # Initialize the list widget and layout
        self.layer_list = QListWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Layers"))
        self.layout.addWidget(self.layer_list)
        self.setLayout(self.layout)

        # Connect layer item change signals
        self.layer_list.itemChanged.connect(self.toggle_layer_visibility)
        self.layer_list.itemClicked.connect(self.on_layer_selected)

        # Populate the list with the current layers
        self.update_layer_list()

    def update_layer_list(self):
        """Refreshes the layer list to reflect the current layers in the image processor."""
        self.layer_list.clear()
        for i, layer in enumerate(self.image_processor.layers):
            layer_item = QListWidgetItem(f"Layer {i + 1} {'(Visible)' if layer.visible else '(Hidden)'}")
            layer_item.setCheckState(Qt.Checked if layer.visible else Qt.Unchecked)
            self.layer_list.addItem(layer_item)

    def on_layer_selected(self, item):
        """Sets the selected layer as the active layer in the image processor."""
        index = self.layer_list.row(item)
        self.image_processor.set_active_layer(index)

    def toggle_layer_visibility(self, item):
        """Toggles the visibility of the layer based on the check state."""
        index = self.layer_list.row(item)
        self.image_processor.toggle_layer_visibility(index)
        self.update_layer_list()
