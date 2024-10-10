from src.ScreenshotApp import ScreenshotApp
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == '__main__':
    Qapp = QApplication(sys.argv)
    app = ScreenshotApp()
    app.show()
    sys.exit(Qapp.exec_())
