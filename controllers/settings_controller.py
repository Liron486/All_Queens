from PyQt5.QtCore import QObject, pyqtSignal
from utils import resize_and_show_normal
from models.settings_model import SettingsModel
from views.settings_view import SettingsWindow
from logger import get_logger

class SettingsController(QObject):
    """
    Controls the settings view and updates the model based on user interactions.
    Also manages the transition from settings to starting the game.
    """
    
    start_game_signal = pyqtSignal()

    def __init__(self, model, view):
        """
        Initializes the SettingsController with the provided model and view.

        Args:
            model (SettingsModel): The model representing the settings.
            view (SettingsWindow): The view for the settings.
        """
        super().__init__()
        self._logger = get_logger(self.__class__.__name__)
        self._model = model
        self._view = view
        self._setup_connections()

    def show_full_screen(self):
        """
        Displays the settings view in full-screen mode.
        """
        self._view.show()
        self._view.showFullScreen()

    def hide_screen(self):
        """
        Hides the settings view.
        """
        self._view.hide()

    def start_game(self):
        """
        Emits a signal to start the game when the play button is clicked.
        """
        self.start_game_signal.emit()

    def exit_full_screen(self):
        """
        Exits full-screen mode and resizes the view to its normal size.
        """
        self._logger.debug("Exit full screen")
        resize_and_show_normal(self._view)

    def set_number_of_real_players(self, number):
        """
        Updates the number of real players in the settings model.

        Args:
            number (int): The number of real players.
        """
        self._logger.debug(f"Number of real players changed to {number}")
        self._model.set_setting("num_real_players", int(number))

    def set_difficulty(self, difficulty, idx):
        """
        Updates the difficulty level for a specific player in the settings model.

        Args:
            difficulty (str): The difficulty level.
            idx (int): The index of the player (0 for the first player, 1 for the second).
        """
        if idx == 0:
            self._logger.debug(f"Difficulty changed to {difficulty}")
        else:
            self._logger.debug(f"Difficulty of the second player changed to {difficulty}")

        difficulty_settings = self._model.get_setting('difficulty')
        difficulty_settings[idx] = difficulty
        self._model.set_setting("difficulty", difficulty_settings)

    def set_is_starting(self, start):
        """
        Updates the starting player preference in the settings model.

        Args:
            start (str): A string indicating whether the player wants to start ("Yes" or "No").
        """
        is_starting = start == "Yes"
        self._logger.debug(f"Player changed the 'want to start' option to {is_starting}")
        self._model.set_setting("is_starting", is_starting)

    def set_name(self, new_name, idx):
        """
        Updates the name of a specific player in the settings model.

        Args:
            new_name (str): The new name of the player.
            idx (int): The index of the player (0 for the first player, 1 for the second).
        """
        position = "First" if idx == 0 else "Second"
        self._logger.debug(f"{position} player name changed to {new_name}")
        names_settings = self._model.get_setting('names')
        names_settings[idx] = new_name
        self._model.set_setting('names', names_settings)

    def _setup_connections(self):
        """
        Sets up the signal-slot connections between the view and the controller.
        """
        self._view.exit_full_screen_signal.connect(self.exit_full_screen)
        self._view.number_of_players_changed.connect(self.set_number_of_real_players)
        self._view.difficulty_changed.connect(self.set_difficulty)
        self._view.name_changed.connect(self.set_name)
        self._view.starting_player_changed.connect(self.set_is_starting)
        self._view.play_clicked.connect(self.start_game)
