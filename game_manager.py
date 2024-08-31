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
        self.app = QApplication([])
        self.logger = get_logger(self.__class__.__name__)

        # Models
        self.settings_model = SettingsModel()

        # Views
        self.welcome_view = WelcomeWindow()
        self.settings_view = SettingsWindow()

        # Controllers
        self.settings_controller = SettingsController(self.settings_model, self.settings_view)
        self.welcome_controller = WelcomeController(self.welcome_view)

        self._setup_connections()

    def start_game(self):
        """
        Starts the game by initializing the game state, game view, and game controller.
        Hides the settings view and displays the game in full-screen mode.
        """
        self.logger.debug("Starting the Game!")
        self.game_state = GameState(self.settings_model)
        self.game_view = GameWindow(self.game_state.get_players(), self.game_state.get_game_number(), self.game_state.get_board())
        self.game_controller = GameController(self.game_state, self.game_view)
        self.settings_view.hide()
        self.game_controller.show_full_screen()

    def show_settings(self):
        """
        Switches from the welcome view to the settings view, displaying the settings window in full-screen mode.
        """
        self.logger.debug("Switching to settings window")
        self.welcome_controller.hide_screen()
        self.settings_controller.show_full_screen()

    def load_game(self):
        """
        Loads and starts the game by showing the welcome view and starting the application's event loop.
        """
        self.logger.debug("Game Starts!")
        self.welcome_controller.show_full_screen()
        self.app.exec_()

    def _setup_connections(self):
        """
        Sets up the connections between controllers and their respective signals.
        """
        self.welcome_controller.request_settings_view_signal.connect(self.show_settings)
        self.settings_controller.start_game_signal.connect(self.start_game)
