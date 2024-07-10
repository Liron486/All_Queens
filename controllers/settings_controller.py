from PyQt5.QtCore import QObject, pyqtSignal
from utils import resize_and_show_normal
from models.settings_model import SettingsModel
from views.settings_view import SettingsWindow
from logger import get_logger

class SettingsController(QObject):
    start_game_signal = pyqtSignal()

    def __init__(self, model, view):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        self.model = model
        self.view = view
        self.setup_connections()

    def setup_connections(self):
        self.view.exit_full_screen_signal.connect(self.exit_full_screen)
        self.view.number_of_players_changed.connect(self.set_number_of_real_players)
        self.view.difficulty_changed.connect(self.set_difficulty)
        self.view.name_changed.connect(self.set_name)
        self.view.starting_player_changed.connect(self.set_is_starting)
        self.view.play_clicked.connect(self.start_game)

    def show_full_screen(self):
        self.view.showFullScreen()

    def exit_full_screen(self):
        self.logger.debug("Exit full screen")
        resize_and_show_normal(self.view)

    def set_number_of_real_players(self, number):
        self.logger.debug(f"Number of real players changed to {number}")
        self.model.set_setting("num_real_players", int(number))

    def set_difficulty(self, difficulty):
        self.logger.debug(f"Difficulty changed to {difficulty}")
        self.model.set_setting("difficulty", difficulty)

    def set_is_starting(self, start):
        is_starting = start == "Yes"
        self.logger.debug(f"Player change the want to start option to {is_starting}")
        self.model.set_setting("is_starting", is_starting)

    def set_name(self, new_name, idx):
        position = "First" if idx == 0 else "Second"
        self.logger.debug(f"{position} player name changed to {new_name}")
        names_settings = self.model.get_setting('names')
        names_settings[idx] = new_name
        self.model.set_setting('names', names_settings)

    def start_game(self):
        self.start_game_signal.emit()






