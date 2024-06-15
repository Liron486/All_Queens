from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QSizePolicy, QHBoxLayout, QApplication, QSpacerItem
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from utils import BackgroundWindow
from logger import get_logger

class SettingsWindow(BackgroundWindow):
    exit_full_screen_signal = pyqtSignal()
    number_of_players_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__('resources/images/settings_background.png')
        self.logger = get_logger(self.__class__.__name__)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('4 Queens')
        self.create_main_layout()
        self.create_number_of_players_ui()

    def create_main_layout(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setAlignment(Qt.AlignCenter)

    def create_number_of_players_ui(self):
        # Create the label
        num_players_layout = QHBoxLayout()
        label = QLabel("Number of real players:")
        label.setStyleSheet("color: black;")
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) 
        num_players_layout.addWidget(label)

        # Create the horizontal layout for buttons
        button_layout = QHBoxLayout()
        button1 = None
        for i in range(3):
            button = QPushButton(str(i))
            button.setCheckable(True)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.clicked.connect(self.on_button_clicked)
            button_layout.addWidget(button)  # Add buttons to the horizontal layout
            if i == 1:
                button1 = button

        num_players_layout.addLayout(button_layout)
        self.main_layout.addLayout(num_players_layout)
        button1.click()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_num_of_players_row()

    def adjust_num_of_players_row(self):
        main_layout_item = self.main_layout.itemAt(0)
        if main_layout_item is None:
            return
        num_players_layout = main_layout_item.layout()

        label_item = num_players_layout.itemAt(0)
        label = label_item.widget()
        font_size = min(self.width(), self.height()) * 0.006
        label.setFont(QFont('Arial', int(font_size)))
        label.adjustSize()

        button_width_size = self.width() * 0.0405
        button_height_size = self.height() * 0.027
        font_size = int(min(button_width_size, button_height_size) * 0.2)

        button_layout_item = num_players_layout.itemAt(1)
        button_layout = button_layout_item.layout()
        for i in range(button_layout.count()):
            button_item = button_layout.itemAt(i)
            button = button_item.widget()
            button.setFixedSize(int(button_width_size), int(button_height_size))
            button.setFont(QFont('Arial', int(font_size)))


    def on_button_clicked(self):
        sender = self.sender()
        # Access the button layout from the main layout
        main_layout_item = self.main_layout.itemAt(0)
        num_players_layout = main_layout_item.layout()
        button_layout_item = num_players_layout.itemAt(1)
        button_layout = button_layout_item.layout()
        for i in range(button_layout.count()):
            button_item = button_layout.itemAt(i)
            button = button_item.widget()
            if button is sender:
                button.setStyleSheet("background-color: lightblue")
                self.number_of_players_changed.emit(int(button.text()))  # Emit signal
            else:
                button.setChecked(False)
                button.setStyleSheet("")


    def keyPressEvent(self, event):
        self.logger.debug(f"Key pressed - {event.key()}")
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()
