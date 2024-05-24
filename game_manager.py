from PyQt5.QtWidgets import QApplication
from controllers.welcome_controller import WelcomeController
from controllers.settings_controller import SettingsController
from views.welcome_view import WelcomeWindow
from views.settings_view import SettingsWindow
from models.settings_model import SettingsModel

class GameManager:
    def __init__(self):
        self.app = QApplication([])

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
        self.welcome_view.hide()
        self.settings_view.show()
        self.settings_view.show_full_screen()

    def start_game(self):
        self.welcome_controller.show_welcome()
        self.app.exec_()

