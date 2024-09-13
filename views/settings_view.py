import sys
import os
from ctypes import windll, c_void_p
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QSizePolicy, QHBoxLayout, QApplication, QSpacerItem, QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from utils import BackgroundWindow, resource_path, DEFAULT_FONT
from logger import get_logger

# Constants
SETTINGS_BACKGROUND_IMAGE_PATH = resource_path('resources/images/settings_background.png')

# Layout item indices
TITLE_LABEL_INDEX = 1
NUM_PLAYERS_INDEX = 3
PLAYER_NAMES_INDEX = 5
DIFFICULTY1_INDEX = 7
DIFFICULTY2_INDEX = 9
STARTING_PLAYER_INDEX = 10
PLAY_BUTTON_INDEX = 11

# Text Labels
starting_layer_text = "Do you want to start? "
default_difficulty_text = "Difficulty:"
difficulty_text_first_player = "Difficulty of The First Player:"
difficulty_text_second_player = "Difficulty of The Second Player:"

# Ratio Constants for layout
TOP_SPACER_HEIGHT_RATIO = 0.3
TITLE_SPACER_HEIGHT_RATIO = 0.05
LINE_SPACER_HEIGHT_RATIO = 0.01
END_SPACER_HEIGHT_RATIO = 0.28
BUTTON_WIDTH_RATIO = 0.0405
BUTTON_HEIGHT_RATIO = 0.027
TEXTBOX_WIDTH_RATIO = 0.085
TEXTBOX_HEIGHT_RATIO = 0.025
PLAY_BUTTON_WIDTH_RATIO = 0.03
PLAY_BUTTON_HEIGHT_RATIO = 0.05

def get_window_dpi(window):
    """
    Retrieves the DPI of the given window.

    Args:
        window (QWidget): The window for which to get the DPI.

    Returns:
        int: The DPI of the window.
    """
    hwnd = c_void_p(int(window.winId()))
    return windll.user32.GetDpiForWindow(hwnd)

def get_sender_layout(sender):
    """
    Retrieves the layout containing the sender widget.

    Args:
        sender (QWidget): The widget that sent the signal.

    Returns:
        QHBoxLayout: The layout containing the sender widget.
    """
    parent = sender.parentWidget()
    layout = parent.layout()
    if layout is not None:
        for i in range(layout.count()):
            item = layout.itemAt(i)
            child_layout = item.layout()
            if isinstance(child_layout, QHBoxLayout):
                for j in range(child_layout.count()):
                    sub_item = child_layout.itemAt(j)
                    sub_layout = sub_item.layout()
                    if isinstance(sub_layout, QHBoxLayout):
                        for k in range(sub_layout.count()):
                            if sub_layout.itemAt(k).widget() == sender:
                                return sub_layout
    return None

def update_buttons(sender):
    """
    Updates the state of buttons in the same layout as the sender, highlighting the clicked button.

    Args:
        sender (QPushButton): The button that was clicked.
    """
    button_layout = get_sender_layout(sender)
    for i in range(button_layout.count()):
        button_item = button_layout.itemAt(i)
        button = button_item.widget()
        button.setChecked(False)
        button.setStyleSheet("")
        if button is sender:
            button.setStyleSheet("background-color: lightblue")

def set_layout_visibility(layout, visible, visible_text):
    """
    Sets the visibility of the widgets in the given layout.

    Args:
        layout (QLayout): The layout whose widgets' visibility to set.
        visible (bool): Whether the widgets should be visible.
        visible_text (str): The text to display if the widgets are visible.
    """
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is not None:
            widget = item.widget()
            if widget is not None:
                if isinstance(widget, QLabel):
                    widget.setText(visible_text if visible else "")
                else:
                    widget.setVisible(visible)
            elif item.layout() is not None:
                sub_layout = item.layout()
                set_layout_visibility(sub_layout, visible, visible_text)

class SettingsWindow(BackgroundWindow):
    """
    Represents the settings window where users can configure game options before starting the game.
    """

    exit_full_screen_signal = pyqtSignal()
    number_of_players_changed = pyqtSignal(str)
    difficulty_changed = pyqtSignal(str, int)
    name_changed = pyqtSignal(str, int)
    starting_player_changed = pyqtSignal(str)
    play_clicked = pyqtSignal()

    def __init__(self):
        """
        Initializes the SettingsWindow with the settings background image.
        """
        super().__init__(SETTINGS_BACKGROUND_IMAGE_PATH)
        self._logger = get_logger(self.__class__.__name__)
        self._init_ui()

    def _init_ui(self):
        """
        Initializes the user interface components for the settings window.
        """
        self.setWindowTitle('4 Queens')
        self._create_main_layout()

        self._top_spacer = self._add_spacer()
        self._create_title()
        self._title_spacer = self._add_spacer()
        self._create_buttom_list("Number of Real Players:", ["0", "1", "2"], self._change_number_of_players, 1)
        self._line_spacer1 = self._add_spacer()
        self._create_player_names_ui()
        self._line_spacer2 = self._add_spacer()
        self._create_buttom_list(default_difficulty_text, ["Easy", "Medium", "Hard"], self._change_difficulty1)
        self._line_spacer3 = self._add_spacer()
        self._create_buttom_list(difficulty_text_second_player, ["Easy", "Medium", "Hard"], self._change_difficulty2)
        self._create_buttom_list(starting_layer_text, ["Yes", "No"], self._change_starting_player)
        self._create_play_button()
        self._end_spacer = self._add_spacer()
        self._adjust_section_visibility("1")

    def _add_spacer(self):
        """
        Adds a spacer item to the main layout.

        Returns:
            QSpacerItem: The added spacer item.
        """
        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._main_layout.addItem(spacer)
        return spacer

    def _create_main_layout(self):
        """
        Creates the main layout for the settings window.
        """
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self._main_layout = QVBoxLayout(central_widget)
        self._main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

    def _create_title(self):
        """
        Creates the title label for the settings window.
        """
        title_label = QLabel("Settings:")
        title_label.setStyleSheet("color: black; font-weight: bold; text-decoration: underline;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self._main_layout.addWidget(title_label)

    def _create_play_button(self):
        """
        Creates the play button that starts the game.
        """
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
        play_button.clicked.connect(self._start_to_play)
        button_layout.addWidget(play_button, alignment=Qt.AlignCenter)

        self._main_layout.addLayout(button_layout)

    def _create_buttom_list(self, label_text, buttons_text, callback_function, clicked_idx=0):
        """
        Creates a list of buttons with a label.

        Args:
            label_text (str): The text for the label.
            buttons_text (list): A list of button labels.
            callback_function (function): The function to call when a button is clicked.
            clicked_idx (int, optional): The index of the button to click by default. Defaults to 0.
        """
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
        self._main_layout.addLayout(buttons_layout)
        click_button.click()

    def _create_player_names_ui(self):
        """
        Creates the UI components for entering player names.
        """
        player_names_layout = QVBoxLayout()

        # Create and add player name inputs
        self._add_player_name_input(player_names_layout, "First Player Name:", "Player1", 0)
        self._add_player_name_input(player_names_layout, "Second Player Name:", "Player2", 1)

        self._main_layout.addLayout(player_names_layout)

    def _add_player_name_input(self, layout, label_text, input_attr_name, player_index):
        """
        Adds a player name input field to the specified layout.

        Args:
            layout (QVBoxLayout): The layout to add the input field to.
            label_text (str): The text for the label.
            input_attr_name (str): The attribute name for storing the input field.
            player_index (int): The index of the player.
        """
        player_layout = QHBoxLayout()

        player_label = QLabel(label_text)
        player_label.setStyleSheet("color: black;")
        player_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        player_layout.addWidget(player_label)

        player_input = QLineEdit()
        player_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        player_input.setMaxLength(12)
        player_input.setText(input_attr_name)
        player_input.textChanged.connect(lambda text: self._player_name_changed(text, player_index))
        player_layout.addWidget(player_input)

        layout.addLayout(player_layout)
        setattr(self, input_attr_name, player_input)

    def _player_name_changed(self, new_text, player_index):
        """
        Emits a signal when a player name is changed.

        Args:
            new_text (str): The new player name.
            player_index (int): The index of the player.
        """
        self.name_changed.emit(new_text, player_index)

    def resizeEvent(self, event):
        """
        Handles the resize event, adjusting UI components based on the new size.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        self._adjust_title()
        self._adjust_spacers()
        self._adjust_label_and_buttons(NUM_PLAYERS_INDEX)
        self._adjust_players_names()
        self._adjust_label_and_buttons(DIFFICULTY1_INDEX)
        self._adjust_label_and_buttons(DIFFICULTY2_INDEX)
        self._adjust_label_and_buttons(STARTING_PLAYER_INDEX)
        self._adjust_play_button()

    def _adjust_play_button(self):
        """
        Adjusts the size and font of the play button based on the window size.
        """
        main_layout_item = self._main_layout.itemAt(PLAY_BUTTON_INDEX)
        play_button_layout = main_layout_item.layout()
        play_button_item = play_button_layout.itemAt(0)
        play_button = play_button_item.widget()
        scaling_factor = self._get_button_scaling_factor()
        button_width_size = self.width() * PLAY_BUTTON_HEIGHT_RATIO * scaling_factor
        button_height_size = self.height() * PLAY_BUTTON_WIDTH_RATIO * scaling_factor
        font_size = int(min(button_width_size, button_height_size) * self._get_font_scaling_factor())

        play_button.setFixedSize(int(button_width_size), int(button_height_size))
        play_button.setFont(QFont(DEFAULT_FONT, int(font_size)))

    def _adjust_spacers(self):
        """
        Adjusts the height of spacer items based on the window size.
        """
        top_spacer_height = self.height() * TOP_SPACER_HEIGHT_RATIO
        title_spacer_height = self.height() * TITLE_SPACER_HEIGHT_RATIO
        line_spacer_height = self.height() * LINE_SPACER_HEIGHT_RATIO
        end_spacer_height = self.height() * END_SPACER_HEIGHT_RATIO

        self._top_spacer.changeSize(0, int(top_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._title_spacer.changeSize(0, int(title_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._line_spacer1.changeSize(0, int(line_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._line_spacer2.changeSize(0, int(line_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._line_spacer3.changeSize(0, int(line_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._end_spacer.changeSize(0, int(end_spacer_height), QSizePolicy.Minimum, QSizePolicy.Fixed)

        self._main_layout.invalidate()  

    def _adjust_title(self):
        """
        Adjusts the title label based on the window size.
        """
        title = self._main_layout.itemAt(TITLE_LABEL_INDEX)
        self._update_label_size(title, True)

    def _adjust_players_names(self):
        """
        Adjusts the player name labels and input fields based on the window size.
        """
        main_layout_item = self._main_layout.itemAt(PLAYER_NAMES_INDEX)
        players_names_layout = main_layout_item.layout()

        first_player_item = players_names_layout.itemAt(0)
        first_player_label_item = first_player_item.itemAt(0)
        self._update_label_size(first_player_label_item)

        first_player_textbox_item = first_player_item.itemAt(1)
        first_player_textbox = first_player_textbox_item.widget()
        scaling_factor = self._get_button_scaling_factor()
        box_width_size = self.width() * TEXTBOX_WIDTH_RATIO * scaling_factor
        box_height_size = self.height() * TEXTBOX_HEIGHT_RATIO * scaling_factor
        first_player_textbox.setFixedSize(int(box_width_size), int(box_height_size))
        textbox_font_size = int(box_height_size) * self._get_font_scaling_factor()
        first_player_textbox.setFont(QFont(DEFAULT_FONT, int(textbox_font_size)))

        second_player_item = players_names_layout.itemAt(1)
        second_player_label_item = second_player_item.itemAt(0)
        self._update_label_size(second_player_label_item)

        second_player_textbox_item = second_player_item.itemAt(1)
        second_player_textbox = second_player_textbox_item.widget()
        second_player_textbox.setFixedSize(int(box_width_size), int(box_height_size))
        second_player_textbox.setFont(QFont(DEFAULT_FONT, textbox_font_size))

    def _adjust_label_and_buttons(self, main_layout_idx):
        """
        Adjusts the size and font of labels and buttons based on the window size.

        Args:
            main_layout_idx (int): The index of the layout item in the main layout.
        """
        main_layout_item = self._main_layout.itemAt(main_layout_idx)
        num_players_layout = main_layout_item.layout()

        label_item = num_players_layout.itemAt(0)
        self._update_label_size(label_item)

        # Get DPI scaling factor using the helper function
        scaling_factor = self._get_button_scaling_factor()

        # Calculate button size
        button_width_size = self.width() * BUTTON_WIDTH_RATIO * scaling_factor
        button_height_size = self.height() * BUTTON_HEIGHT_RATIO * scaling_factor
        font_size = int(min(button_width_size, button_height_size) * self._get_font_scaling_factor())

        button_layout_item = num_players_layout.itemAt(1)
        button_layout = button_layout_item.layout()
        for i in range(button_layout.count()):
            button_item = button_layout.itemAt(i)
            button = button_item.widget()
            button.setFixedSize(int(button_width_size), int(button_height_size))
            button.setFont(QFont(DEFAULT_FONT, int(font_size)))

    def _adjust_section_visibility(self, num_real_players):
        """
        Adjusts the visibility of sections based on the number of real players selected.

        Args:
            num_real_players (str): The number of real players as a string.
        """
        layout_configs = [
            (DIFFICULTY1_INDEX, num_real_players != "2", difficulty_text_first_player if num_real_players == "0" else default_difficulty_text),
            (DIFFICULTY2_INDEX, num_real_players == "0", difficulty_text_second_player),
            (STARTING_PLAYER_INDEX, num_real_players == "1", starting_layer_text),
        ]

        for layout_idx, visibility_condition, text in layout_configs:
            layout_item = self._main_layout.itemAt(layout_idx)
            if layout_item:
                layout = layout_item.layout()
                if layout:
                    set_layout_visibility(layout, visibility_condition, text)

    def _change_number_of_players(self):
        """
        Changes the number of players based on the button clicked.
        """
        sender = self.sender()
        update_buttons(sender)
        self.number_of_players_changed.emit(sender.text())
        self._adjust_section_visibility(sender.text())

    def _change_difficulty1(self):
        """
        Changes the difficulty for the first player based on the button clicked.
        """
        sender = self.sender()
        update_buttons(sender)
        self.difficulty_changed.emit(sender.text(), 0)

    def _change_difficulty2(self):
        """
        Changes the difficulty for the second player based on the button clicked.
        """
        sender = self.sender()
        update_buttons(sender)
        self.difficulty_changed.emit(sender.text(), 1)

    def _change_starting_player(self):
        """
        Changes the starting player based on the button clicked.
        """
        sender = self.sender()
        update_buttons(sender)
        self.starting_player_changed.emit(sender.text())

    def _update_label_size(self, label_item, is_title=False):
        """
        Updates the size and font of a label based on the window size.

        Args:
            label_item (QWidgetItem): The label item to update.
            is_title (bool, optional): Whether the label is a title. Defaults to False.
        """
        label = label_item.widget()
        width = self.width()
        height = self.height()
        font_size = min(width, height) * self._get_label_scaling_factor(is_title)
        label.setFont(QFont(DEFAULT_FONT, int(font_size)))
        label.adjustSize()

    def keyPressEvent(self, event):
        """
        Handles key press events for the settings window.

        Args:
            event (QKeyEvent): The key press event.
        """
        self._logger.debug(f"Key pressed - {event.key()}")
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self._start_to_play()

    def _start_to_play(self):
        """
        Emits the play_clicked signal when the play button is pressed.
        """
        self._logger.debug("Play! pressed")
        self.play_clicked.emit()

    def _get_button_scaling_factor(self):
        """
        Calculates the button scaling factor based on the window's DPI.

        Returns:
            float: The button scaling factor.
        """
        dpi = get_window_dpi(self)
        return (1 / (dpi / 240.0)) ** 0.25

    def _get_font_scaling_factor(self):
        """
        Calculates the font scaling factor based on the window's DPI.

        Returns:
            float: The font scaling factor.
        """
        dpi = get_window_dpi(self)
        return ((1 / (dpi / 240.0)) ** 0.5) / 5

    def _get_label_scaling_factor(self, is_title):
        """
        Calculates the label scaling factor based on the window's DPI.

        Args:
            is_title (bool): Whether the label is a title.

        Returns:
            float: The label scaling factor.
        """
        dpi = get_window_dpi(self)
        scaling_factor = 1.5 if is_title else 1  
        return (((1 / (dpi / 240.0)) ** 0.85) / 167) * scaling_factor
