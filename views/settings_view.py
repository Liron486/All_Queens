from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QSizePolicy, QHBoxLayout, QApplication, QSpacerItem, QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from utils import BackgroundWindow
from logger import get_logger

def update_buttons(button_layout, sender):
    for i in range(button_layout.count()):
        button_item = button_layout.itemAt(i)
        button = button_item.widget()
        button.setChecked(False)
        button.setStyleSheet("")
        if button is sender:
            button.setStyleSheet("background-color: lightblue")

def set_layout_visibility(layout, visible):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is not None:
            widget = item.widget()
            if widget is not None:
                if isinstance(widget, QLabel):
                    widget.setText("Difficulty:" if visible else "")
                else:
                    widget.setVisible(visible)
            elif item.layout() is not None:
                sub_layout = item.layout()
                set_layout_visibility(sub_layout, visible)


class SettingsWindow(BackgroundWindow):
    exit_full_screen_signal = pyqtSignal()
    number_of_players_changed = pyqtSignal(str)
    difficulty_changed = pyqtSignal(str)
    name_changed = pyqtSignal(str, int)
    play_clicked = pyqtSignal()

    def __init__(self):
        super().__init__('resources/images/settings_background.png')
        self.logger = get_logger(self.__class__.__name__)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('4 Queens')
        self.create_main_layout()

        self.top_spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.main_layout.addItem(self.top_spacer)

        self.create_title()

        self.title_spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.main_layout.addItem(self.title_spacer)

        self.create_buttom_list("Number of Real Players:", ["0", "1", "2"], self.change_number_of_players, 1)

        self.line_spacer1 = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.main_layout.addItem(self.line_spacer1)

        self.create_player_names_ui()

        self.line_spacer2 = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.main_layout.addItem(self.line_spacer2)

        self.create_buttom_list("Difficulty:", ["Easy", "Medium", "Hard"], self.change_difficulty)

        self.line_spacer3 = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.main_layout.addItem(self.line_spacer3)

        self.create_play_button()

        self.end_spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.main_layout.addItem(self.end_spacer)

    def create_main_layout(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

    def create_title(self):
        title_label = QLabel("Settings:")
        title_label.setStyleSheet("color: black; font-weight: bold; text-decoration: underline;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.main_layout.addWidget(title_label)

    def create_play_button(self):
        button_layout = QHBoxLayout()
        play_button = QPushButton("Play!")
        play_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        play_button.setStyleSheet("""
            QPushButton {
                background-color: green;
                color: white;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: darkgreen;
            }
        """)
        play_button.clicked.connect(self.start_to_play)
        button_layout.addWidget(play_button, alignment=Qt.AlignCenter)

        self.main_layout.addLayout(button_layout)

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
        player_names_layout = QVBoxLayout()

        # Create and add player name inputs
        self.add_player_name_input(player_names_layout, "First Player Name:", "Player1", 0)
        self.add_player_name_input(player_names_layout, "Second Player Name:", "Player2", 1)

        self.main_layout.addLayout(player_names_layout)

    def add_player_name_input(self, layout, label_text, input_attr_name, player_index):
        player_layout = QHBoxLayout()

        player_label = QLabel(label_text)
        player_label.setStyleSheet("color: black;")
        player_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        player_layout.addWidget(player_label)

        player_input = QLineEdit()
        player_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        player_input.setMaxLength(12)
        player_input.setText(input_attr_name)
        player_input.textChanged.connect(lambda text: self.player_name_changed(text, player_index))
        player_layout.addWidget(player_input)

        layout.addLayout(player_layout)
        setattr(self, input_attr_name, player_input)

    def player_name_changed(self, new_text, player_index):
        self.name_changed.emit(new_text, player_index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_title()
        self.adjust_spacers()
        self.adjust_label_and_buttons(3)
        self.adjust_players_names()
        self.adjust_label_and_buttons(7)
        self.adjust_play_button()

    def adjust_play_button(self):
        main_layout_item = self.main_layout.itemAt(9)
        play_button_layout = main_layout_item.layout()
        play_button_item = play_button_layout.itemAt(0)
        play_button = play_button_item.widget()
        button_width_size = self.width() * 0.05
        button_height_size = self.height() * 0.03
        font_size = int(min(button_width_size, button_height_size) * 0.2)

        play_button.setFixedSize(int(button_width_size), int(button_height_size))
        play_button.setFont(QFont('Arial', int(font_size)))

    def adjust_spacers(self):
        top_spacer_height = self.height() * 0.3
        title_spacer_height = self.height() * 0.05
        line_spacer_height = self.height() * 0.01
        end_spacer_height = self.height() * 0.22

        self.top_spacer.changeSize(0, int(top_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.title_spacer.changeSize(0, int(title_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.line_spacer1.changeSize(0, int(line_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.line_spacer2.changeSize(0, int(line_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.line_spacer3.changeSize(0, int(line_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.end_spacer.changeSize(0, int(end_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.main_layout.invalidate()  

    def adjust_title(self):
        title = self.main_layout.itemAt(1)
        self.update_label_size(title, True)

    def adjust_players_names(self):
        main_layout_item = self.main_layout.itemAt(5)
        players_names_layout = main_layout_item.layout()

        first_player_item = players_names_layout.itemAt(0)
        first_player_label_item = first_player_item.itemAt(0)
        self.update_label_size(first_player_label_item)

        first_player_textbox_item = first_player_item.itemAt(1)
        first_player_textbox = first_player_textbox_item.widget()
        box_width_size = self.width() * 0.085
        box_height_size = self.height() * 0.025
        first_player_textbox.setFixedSize(int(box_width_size), int(box_height_size))
        textbox_font_size = int(box_height_size) * 0.22
        first_player_textbox.setFont(QFont('Arial', int(textbox_font_size)))

        second_player_item = players_names_layout.itemAt(1)
        second_player_label_item = second_player_item.itemAt(0)
        self.update_label_size(second_player_label_item)

        second_player_textbox_item = second_player_item.itemAt(1)
        second_player_textbox = second_player_textbox_item.widget()
        second_player_textbox.setFixedSize(int(box_width_size), int(box_height_size))
        second_player_textbox.setFont(QFont('Arial', textbox_font_size))

    def adjust_label_and_buttons(self, main_layout_idx):
        main_layout_item = self.main_layout.itemAt(main_layout_idx)
        num_players_layout = main_layout_item.layout()

        label_item = num_players_layout.itemAt(0)
        self.update_label_size(label_item)

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
        main_layout_nplayers_item = self.main_layout.itemAt(3)
        num_players_layout = main_layout_nplayers_item.layout()
        button_layout_item = num_players_layout.itemAt(1)
        button_layout = button_layout_item.layout()

        update_buttons(button_layout, sender)
        self.number_of_players_changed.emit(sender.text())

        # Show or hide the difficulty section based on the number of players selected
        main_layout_difficulty_item = self.main_layout.itemAt(7)
        if main_layout_difficulty_item is not None:
            difficulty_layout = main_layout_difficulty_item.layout()
            if difficulty_layout is not None:
                set_layout_visibility(difficulty_layout, sender.text() != "2")

    def change_difficulty(self):
        sender = self.sender()
        main_layout_item = self.main_layout.itemAt(7)
        num_players_layout = main_layout_item.layout()
        button_layout_item = num_players_layout.itemAt(1)
        button_layout = button_layout_item.layout()

        update_buttons(button_layout, sender)
        self.difficulty_changed.emit(sender.text())

    def update_label_size(self, label_item, is_title=False):
        label = label_item.widget()
        font_size = min(self.width(), self.height()) * 0.006

        if is_title:
            font_size *= 1.5

        label.setFont(QFont('Arial', int(font_size)))
        label.adjustSize()

    def keyPressEvent(self, event):
        self.logger.debug(f"Key pressed - {event.key()}")
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()

    def start_to_play(self):
        self.logger.debug("Play! pressed")
        self.play_clicked.emit()
