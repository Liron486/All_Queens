from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap

class WelcomeWindow(QMainWindow):
    exit_full_screen_signal = pyqtSignal()
    switch_to_settings_signal = pyqtSignal()
    background_path = 'resources/images/welcome_background.png'

    def __init__(self):
        super().__init__()
        self.controller = None
        self.background_label = QLabel(self) 
        self.init_ui()

    def set_controller(self, controller):
        self.controller = controller

    def init_ui(self):
        self.setWindowTitle('4 Queens')
        self.SetBackgroundImage()
        self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()
        else:
            self.switch_to_settings_signal.emit()

    def mousePressEvent(self, event):
        self.switch_to_settings_signal.emit()

    def resizeEvent(self, event):
        super(WelcomeWindow, self).resizeEvent(event)
        if self.background_label:
            self.background_label.setFixedSize(self.size())
            self.background_label.setPixmap(QPixmap(self.background_path).scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    def SetBackgroundImage(self):
        pixmap = QPixmap(self.background_path)
        self.background_label.setPixmap(pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.background_label.setFixedSize(self.size())
        self.background_label.lower()  # Ensure the label is behind all other widgets
