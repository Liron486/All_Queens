from PyQt5.QtCore import pyqtSlot
from utils import resize_and_show_normal
from models.settings_model import SettingsModel
from views.settings_view import SettingsWindow
from logger import get_logger

class SettingsController:
    def __init__(self, model, view):
        self.logger = get_logger(self.__class__.__name__)
        self.model = model
        self.view = view
        self.setup_connections()

    def setup_connections(self):
        self.view.exit_full_screen_signal.connect(self.exit_full_screen)
        self.view.number_of_players_changed.connect(self.set_number_of_real_players)
        self.view.difficulty_changed.connect(self.set_difficulty)

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


