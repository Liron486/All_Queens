import sys
import os
from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from enum import Enum

# Install command for PyInstaller:
# pyinstaller --onefile --windowed --name "4Queens" --add-data "resources/images/*.png;resources/images" --add-data "resources/sounds/*.wav;resources/sounds" main.py

# Constants
DEFAULT_FONT = 'Arial'

def resource_path(relative_path):
    """
    Get the absolute path to the resource, works for development and for PyInstaller.
    
    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
    
# Constants for resource paths
WHITE_PIECE_PATH = resource_path('resources/images/white.png')
BLACK_PIECE_PATH = resource_path('resources/images/black.png')

class PlayerType(Enum):
    """
    Enumeration representing the types of players in the game.
    """
    HUMAN = 0
    AI = 1

class PieceType(Enum):
    """
    Enumeration representing the types of pieces in the game.
    """
    WHITE = 0
    BLACK = 1
    EMPTY = 2

class BackgroundWindow(QMainWindow):
    """
    A QMainWindow subclass that displays a background image, which resizes with the window.
    """

    def __init__(self, background_path, parent=None):
        """
        Initializes the BackgroundWindow with the specified background image.

        Args:
            background_path (str): The path to the background image.
            parent (QWidget, optional): The parent widget, if any.
        """
        super().__init__(parent)
        self._background_path = background_path
        self._background_label = QLabel(self)
        self._set_background_image()

    def resizeEvent(self, event):
        """
        Handles the resize event to ensure the background image scales with the window.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        self._set_background_image()

    def _set_background_image(self):
        """
        Sets the background image for the window, scaling it to fit the window size.
        """
        pixmap = QPixmap(self._background_path)
        self._background_label.setPixmap(pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self._background_label.setFixedSize(self.size())
        self._background_label.lower()

def create_spacer_widget(width, height):
    """
    Creates a spacer widget with the specified width and height.

    Args:
        width (int): The width of the spacer.
        height (int): The height of the spacer.

    Returns:
        QWidget: The created spacer widget.
    """
    spacer = QWidget()
    spacer.setFixedSize(width, height)
    return spacer

def resize_and_show_normal(window):
    """
    Resizes the window to half the screen size and centers it on the screen.

    Args:
        window (QMainWindow): The window to be resized and centered.
    """
    window.setWindowFlags(Qt.Window)
    window.showNormal()
    screen = QApplication.primaryScreen().geometry()
    new_width = screen.width() // 2
    new_height = screen.height() // 2
    new_left = (screen.width() - new_width) // 2
    new_top = (screen.height() - new_height) // 2

    window.resize(new_width, new_height)
    window.move(new_left, new_top)
