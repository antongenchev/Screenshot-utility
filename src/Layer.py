
class Layer:
    def __init__(self, image=None, visible=True):
        self.image = image
        self.visible = visible
        self.drawing_enabled = False

    def toggle_visibility(self):
        self.visible = not self.visible