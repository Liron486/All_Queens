from PyQt5.QtWidgets import QApplication
from controllers.welcome_controller import WelcomeController
from controllers.settings_controller import SettingsController
from controllers.game_controller import GameController
from views.welcome_view import WelcomeWindow
from views.settings_view import SettingsWindow
from views.game_view import GameWindow
from models.settings_model import SettingsModel
from models.game_state import GameState
from logger import get_logger

class GameManager:
    """
    Manages the overall flow of the game, including initializing models, views, 
    and controllers, and handling transitions between different game states.
    """

    def __init__(self):
        """
        Initializes the GameManager by setting up the application, models, views, and controllers.
        """
        self._app = QApplication([])
        self._logger = get_logger(self.__class__.__name__)

        # Models
        self._settings_model = SettingsModel()

        # Views
        self._welcome_view = WelcomeWindow()
        self._settings_view = SettingsWindow()

        # Controllers
        self._settings_controller = SettingsController(self._settings_model, self._settings_view)
        self._welcome_controller = WelcomeController(self._welcome_view)

        self._game_controller = None
        self._game_state = None
        self._game_view = None

        self._setup_connections()

    def start_game(self):
        """
        Starts the game by initializing the game state, game view, and game controller.
        Hides the settings view and displays the game in full-screen mode.
        """
        self._logger.debug("Starting the Game!")
        self._game_state = GameState(self._settings_model)
        self._game_view = GameWindow(self._game_state.players, self._game_state.game_number, self._game_state.board)
        self._game_controller = GameController(self._game_state, self._game_view)
        self._game_controller.back_to_settings_singal.connect(self.show_settings)
        self._settings_controller.hide_screen()
        self._game_controller.show_full_screen()

    def show_settings(self):
        """
        Switches from the welcome view to the settings view, displaying the settings window in full-screen mode.
        """
        self._logger.debug("Switching to settings window")
        if self._game_controller:
            self._game_controller.hide_screen()
            self._game_controller.back_to_settings_singal.disconnect(self.show_settings)
        self._welcome_controller.hide_screen()
        self._settings_controller.show_full_screen()

    def load_game(self):
        """
        Loads and starts the game by showing the welcome view and starting the application's event loop.
        """
        self._logger.debug("Game Starts!")
        self._welcome_controller.show_full_screen()
        self._app.exec_()

    def _setup_connections(self):
        """
        Sets up the connections between controllers and their respective signals.
        """
        self._welcome_controller.request_settings_view_signal.connect(self.show_settings)
        self._settings_controller.start_game_signal.connect(self.start_game)
