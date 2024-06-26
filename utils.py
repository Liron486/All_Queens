from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class BackgroundWindow(QMainWindow):
    def __init__(self, background_path, parent=None):
        super().__init__(parent)
        self.background_path = background_path
        self.background_label = QLabel(self)
        self.init_ui()

    def init_ui(self):
        self.set_background_image()

    def set_background_image(self):
        pixmap = QPixmap(self.background_path)
        self.background_label.setPixmap(pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.background_label.setFixedSize(self.size())
        self.background_label.lower()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_background_image()

def resize_and_show_normal(window):
    window.setWindowFlags(Qt.Window)
    window.showNormal()
    screen = QApplication.primaryScreen().geometry()
    new_width = screen.width() // 2
    new_height = screen.height() // 2
    new_left = (screen.width() - new_width) // 2
    new_top = (screen.height() - new_height) // 2

    window.resize(new_width, new_height)
    window.move(new_left, new_top)