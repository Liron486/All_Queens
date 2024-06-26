from PyQt5.QtWidgets import QApplication
from controllers.welcome_controller import WelcomeController
from controllers.settings_controller import SettingsController
from views.welcome_view import WelcomeWindow
from views.settings_view import SettingsWindow
from models.settings_model import SettingsModel
from logger import get_logger

class GameManager:
    def __init__(self):
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

        self.setup_connections()

    def setup_connections(self):
        self.welcome_controller.request_settings_view_signal.connect(self.show_settings)

    def show_settings(self):
        self.logger.debug("Switching to settings window")
        self.welcome_view.hide()
        self.settings_view.show()
        self.settings_controller.show_full_screen()

    def start_game(self):
        self.logger.debug("Game Starts!")
        self.welcome_controller.show_welcome()
        self.app.exec_()

