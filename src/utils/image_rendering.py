import numpy as np
import cv2
from PyQt5.QtGui import QPixmap, QImage

def qpixmap_to_qimage(pixmap: QPixmap) -> QImage:
    """Convert QPixmap to QImage."""
    return pixmap.toImage()

def qimage_to_cv2(qimage: QImage) -> np.ndarray:
    """Convert QImage to OpenCV (cv2) image."""
    width, height = qimage.width(), qimage.height()
    ptr = qimage.bits()
    ptr.setsize(qimage.byteCount())
    arr = np.array(ptr).reshape((height, width, 4))
    return arr

def qpixmap_to_cv2(pixmap: QPixmap) -> np.ndarray:
    """Convert QPixmap to OpenCV (cv2) image."""
    return qimage_to_cv2(qpixmap_to_qimage(pixmap))
