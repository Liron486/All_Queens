from PyQt5.QtCore import pyqtSignal
from utils import resize_and_show_normal
from models.game_state import GameState
from logger import get_logger

class GameController:
    def __init__(self, game_state, view, is_edit_mode=False):
        self.logger = get_logger(self.__class__.__name__)
        self.state = game_state
        self.view = view       
        self.setup_connections()

    def setup_connections(self):
        self.view.exit_full_screen_signal.connect(self.exit_full_screen)

    def show_full_screen(self):
        self.view.show()
        self.view.showFullScreen()

    def exit_full_screen(self):
        self.logger.debug("Exit full screen")
        resize_and_show_normal(self.view)