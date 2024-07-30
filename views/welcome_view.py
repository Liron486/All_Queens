from PyQt5.QtCore import pyqtSignal, Qt
from utils import BackgroundWindow, resource_path
from logger import get_logger

class WelcomeWindow(BackgroundWindow):
    exit_full_screen_signal = pyqtSignal()
    switch_to_settings_signal = pyqtSignal()

    def __init__(self):
        super().__init__(resource_path('resources/images/welcome_background.png'))
        self.logger = get_logger(self.__class__.__name__)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('4 Queens')

    def keyPressEvent(self, event):
        self.logger.debug(f"Key pressed - {event.key()}")
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()
        else:
            self.switch_to_settings_signal.emit()

    def mousePressEvent(self, event):
        self.logger.debug("Mouse pressed")
        self.switch_to_settings_signal.emit()

