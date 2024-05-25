from PyQt5.QtCore import pyqtSignal, Qt
from utils import BackgroundWindow

class SettingsWindow(BackgroundWindow):
    exit_full_screen_signal = pyqtSignal()

    def __init__(self):
        super().__init__('resources/images/settings_background.png')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('4 Queens')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()
