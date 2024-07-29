from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel, QApplication, QSpacerItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from enum import Enum

WHITE_PIECE_PATH = 'resources/images/white.png'
BLACK_PIECE_PATH = 'resources/images/black.png'

class PlayerType(Enum):
    HUMAN = 0
    AI = 1
    
class PieceType(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2

class BackgroundWindow(QMainWindow):
    def __init__(self, background_path, parent=None):
        super().__init__(parent)
        self.background_path = background_path
        self.background_label = QLabel(self)
        self.set_background_image()

    def set_background_image(self):
        pixmap = QPixmap(self.background_path)
        self.background_label.setPixmap(pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.background_label.setFixedSize(self.size())
        self.background_label.lower()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_background_image()


def create_spacer_widget(width, height):
    spacer = QWidget()
    spacer.setFixedSize(width, height)
    return spacer

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