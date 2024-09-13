from PyQt5.QtCore import pyqtSignal, Qt
from utils import BackgroundWindow, resource_path
from logger import get_logger

WELCOME_BACKGROUND_IMAGE_PATH = resource_path('resources/images/welcome_background.png')

class WelcomeWindow(BackgroundWindow):
    """
    Represents the welcome window of the application, handling user interactions 
    such as key presses and mouse clicks to transition to the settings view.
    """
    
    exit_full_screen_signal = pyqtSignal()
    switch_to_settings_signal = pyqtSignal()

    def __init__(self):
        """
        Initializes the WelcomeWindow with the background image and sets up the UI.
        """
        super().__init__(WELCOME_BACKGROUND_IMAGE_PATH)
        self._logger = get_logger(self.__class__.__name__)
        self._init_ui()

    def keyPressEvent(self, event):
        """
        Handles key press events, emitting signals based on the key pressed.

        Args:
            event (QKeyEvent): The key press event.
        """
        self._logger.debug(f"Key pressed - {event.key()}")
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()
        else:
            self.switch_to_settings_signal.emit()

    def mousePressEvent(self, event):
        """
        Handles mouse press events, emitting a signal to switch to the settings view.

        Args:
            event (QMouseEvent): The mouse press event.
        """
        self._logger.debug("Mouse pressed")
        self.switch_to_settings_signal.emit()

    def _init_ui(self):
        """
        Initializes the UI components for the WelcomeWindow.
        """
        self.setWindowTitle('4 Queens')
