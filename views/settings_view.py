from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QSizePolicy, QHBoxLayout, QApplication, QSpacerItem, QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from utils import BackgroundWindow
from logger import get_logger

def update_buttons(button_layout, sender):
    for i in range(button_layout.count()):
        button_item = button_layout.itemAt(i)
        button = button_item.widget()
        if button is sender:
            button.setStyleSheet("background-color: lightblue")
        else:
            button.setChecked(False)
            button.setStyleSheet("")

class SettingsWindow(BackgroundWindow):
    exit_full_screen_signal = pyqtSignal()
    number_of_players_changed = pyqtSignal(str)
    difficulty_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__('resources/images/settings_background.png')
        self.logger = get_logger(self.__class__.__name__)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('4 Queens')
        self.create_main_layout()
        self.create_buttom_list("Number of Real Players:", ["0", "1", "2"], self.change_number_of_players, 1)
        self.create_player_names_ui()

        spacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.main_layout.addItem(spacer1)

        self.create_buttom_list("Difficulty:", ["Easy", "Medium", "Hard"], self.change_difficulty)

    def create_main_layout(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setAlignment(Qt.AlignCenter)

    def create_buttom_list(self, label_text, buttons_text, callback_function, clicked_idx=0):
        buttons_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("color: black;")
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) 
        buttons_layout.addWidget(label)

        button_layout = QHBoxLayout()
        click_button = None
        for i, text in enumerate(buttons_text):
            button = QPushButton(text)
            button.setCheckable(True)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.clicked.connect(callback_function)
            button_layout.addWidget(button)
            if i == clicked_idx:
                click_button = button

        buttons_layout.addLayout(button_layout)
        self.main_layout.addLayout(buttons_layout)
        click_button.click()

    def create_player_names_ui(self):
        player_names_layout = QHBoxLayout()

        # Create and add player name inputs
        self.add_player_name_input(player_names_layout, "First Player Name:", "Player1")
        self.add_player_name_input(player_names_layout, "Second Player Name:", "Player2")

        self.main_layout.addLayout(player_names_layout)

    def add_player_name_input(self, layout, label_text, input_attr_name):
        player_layout = QHBoxLayout()

        player_label = QLabel(label_text)
        player_label.setStyleSheet("color: black;")
        player_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        player_layout.addWidget(player_label)

        player_input = QLineEdit()
        player_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        player_input.setMaximumWidth(150)
        player_input.setMaxLength(9)
        player_input.setText(input_attr_name)
        player_layout.addWidget(player_input)

        layout.addLayout(player_layout)
        setattr(self, input_attr_name, player_input)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_label_and_buttons(0)
        self.adjust_players_names()
        self.adjust_label_and_buttons(3)

    def adjust_players_names(self):
        main_layout_item = self.main_layout.itemAt(1)
        players_names_layout = main_layout_item.layout()

        first_player_item = players_names_layout.itemAt(0)
        first_player_label_item = first_player_item.itemAt(0)
        first_player_label = first_player_label_item.widget()
        font_size = min(self.width(), self.height()) * 0.006
        first_player_label.setFont(QFont('Arial', int(font_size)))
        first_player_label.adjustSize()

        first_player_textbox_item = first_player_item.itemAt(1)
        first_player_textbox = first_player_textbox_item.widget()
        box_width_size = self.width() * 0.0405
        box_height_size = self.height() * 0.02
        first_player_textbox.setFixedSize(int(box_width_size), int(box_height_size))
        textbox_font_size = int(box_height_size) * 0.22
        first_player_textbox.setFont(QFont('Arial', int(textbox_font_size)))

        second_player_item = players_names_layout.itemAt(1)
        second_player_label_item = second_player_item.itemAt(0)
        second_player_label = second_player_label_item.widget()
        second_player_label.setFont(QFont('Arial', int(font_size)))
        second_player_label.adjustSize()

        second_player_textbox_item = second_player_item.itemAt(1)
        second_player_textbox = second_player_textbox_item.widget()
        second_player_textbox.setFixedSize(int(box_width_size), int(box_height_size))
        second_player_textbox.setFont(QFont('Arial', textbox_font_size))


    def adjust_label_and_buttons(self, main_layout_idx):
        main_layout_item = self.main_layout.itemAt(main_layout_idx)
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

    def change_number_of_players(self):
        sender = self.sender()
        main_layout_item = self.main_layout.itemAt(0)
        num_players_layout = main_layout_item.layout()
        button_layout_item = num_players_layout.itemAt(1)
        button_layout = button_layout_item.layout()

        update_buttons(button_layout, sender)
        self.number_of_players_changed.emit(sender.text())

    def change_difficulty(self):
        sender = self.sender()
        main_layout_item = self.main_layout.itemAt(3)
        num_players_layout = main_layout_item.layout()
        button_layout_item = num_players_layout.itemAt(1)
        button_layout = button_layout_item.layout()

        update_buttons(button_layout, sender)
        self.difficulty_changed.emit(sender.text())

    def keyPressEvent(self, event):
        self.logger.debug(f"Key pressed - {event.key()}")
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()
