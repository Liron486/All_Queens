from PyQt5.QtCore import QObject, pyqtSignal
from utils import resize_and_show_normal

class WelcomeController(QObject):
    request_settings_view_signal = pyqtSignal()

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.setup_connections()
        self.view.showFullScreen()

    def setup_connections(self):
        self.view.exit_full_screen_signal.connect(self.exit_full_screen)
        self.view.switch_to_settings_signal.connect(self.handle_switch_to_settings)

    def handle_switch_to_settings(self):
        self.request_settings_view_signal.emit()

    def show_welcome(self):
        self.view.show()

    def exit_full_screen(self):
        resize_and_show_normal(self.view)
