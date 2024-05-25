from PyQt5.QtCore import pyqtSignal, Qt
from utils import BackgroundWindow

class WelcomeWindow(BackgroundWindow):
    exit_full_screen_signal = pyqtSignal()
    switch_to_settings_signal = pyqtSignal()

    def __init__(self):
        super().__init__('resources/images/welcome_background.png')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('4 Queens')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()
        else:
            self.switch_to_settings_signal.emit()

    def mousePressEvent(self, event):
        self.switch_to_settings_signal.emit()

