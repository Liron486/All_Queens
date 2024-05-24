from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

class SettingsWindow(QWidget):
    exit_full_screen_signal = pyqtSignal()
    background_path = 'resources/images/settings_background.png'

    def __init__(self):
        super().__init__()
        self.controller = None
        self.background_label = QLabel(self) 
        self.init_ui()

    def set_controller(self, controller):
        self.controller = controller

    def show_full_screen(self):
        self.showFullScreen()

    def init_ui(self):
        self.setWindowTitle('4 Queens')
        self.SetBackgroundImage()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()

    def resizeEvent(self, event):
        super(SettingsWindow, self).resizeEvent(event)
        if self.background_label:
            self.background_label.setFixedSize(self.size())
            self.background_label.setPixmap(QPixmap(self.background_path).scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    def SetBackgroundImage(self):
        pixmap = QPixmap(self.background_path)
        self.background_label.setPixmap(pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.background_label.setFixedSize(self.size())
        self.background_label.lower()  # Ensure the label is behind all other widgets