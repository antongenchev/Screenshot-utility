from src.ScreenshotApp import ScreenshotApp
from PyQt5.QtWidgets import QApplication
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == '__main__':
    Qapp = QApplication(sys.argv)
    app = ScreenshotApp()
    app.show()
    sys.exit(Qapp.exec_())
