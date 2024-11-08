from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

class ImageProcessingToolSetting(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.current_settings_widget = None

        # GUI settings
        self.setMinimumSize(300, 200)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def set_tool_settings_ui(self, settings_widget:QWidget):
        # Clear existing settings widget, if any
        if self.current_settings_widget:
            self.layout.removeWidget(self.current_settings_widget)
            self.current_settings_widget.deleteLater()
            self.current_settings_widget = None

        # Add the new settings widget
        if settings_widget:
            self.layout.addWidget(settings_widget)
            self.current_settings_widget = settings_widget