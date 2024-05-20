from views.settings_view import SettingsWindow
from models.settings_model import SettingsModel
from controllers.settings_controller import SettingsController

class WelcomeController:
    def __init__(self, view):
        self.view = view
        self.view.escapePressed.connect(self.exit_full_screen)
        self.settings_window = SettingsWindow()
        self.settings_model = SettingsModel()
        self.settings_controller = SettingsController(self.settings_model, self.settings_window)
        self.settings_window.set_controller(self.settings_controller)

    def show_welcome(self):
        self.view.show()

    def play(self):
        self.view.hide()  # Hide the welcome window
        self.settings_window.show()  # Show the settings window
        self.settings_window.show_full_screen()

    def exit_full_screen(self):
        self.view.showNormal()  # Exits full screen mode
