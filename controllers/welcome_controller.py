from PyQt5.QtCore import QObject, pyqtSignal
from utils import resize_and_show_normal
from logger import get_logger


class WelcomeController(QObject):
    request_settings_view_signal = pyqtSignal()

    def __init__(self, view):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        self.view = view
        self.setup_connections()

    def setup_connections(self):
        self.view.exit_full_screen_signal.connect(self.exit_full_screen)
        self.view.switch_to_settings_signal.connect(self.handle_switch_to_settings)

    def handle_switch_to_settings(self):
        self.request_settings_view_signal.emit()

    def hide_screen(self):
        self.view.hide()
        
    def show_full_screen(self):
        self.view.show()
        self.view.showFullScreen()

    def exit_full_screen(self):
        self.logger.debug("Exit full screen")
        resize_and_show_normal(self.view)
