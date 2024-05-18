from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap

class WelcomeWindow(QMainWindow):
    escapePressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.controller = None  # Initialize controller as None
        self.background_label = QLabel(self)  # Create a label to hold the background image
        self.init_ui()

    def set_controller(self, controller):
        self.controller = controller

    def init_ui(self):
        self.setWindowTitle('Welcome to 4 Queens')
        
        # Set up the background image
        pixmap = QPixmap('resources/images/welcome_background.png')
        self.background_label.setPixmap(pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.background_label.setFixedSize(self.size())
        self.background_label.lower()  # Ensure the label is behind all other widgets

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.escapePressed.emit()  # Emit the signal
        else:
            self.controller.play()

    def resizeEvent(self, event):
        # Update the background label size and pixmap when the window is resized
        super(WelcomeWindow, self).resizeEvent(event)
        if self.background_label:
            self.background_label.setFixedSize(self.size())
            self.background_label.setPixmap(QPixmap('resources/images/welcome_background.png').scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
