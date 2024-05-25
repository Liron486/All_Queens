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

    def show_full_screen(self):
        self.view.showFullScreen()

    @pyqtSlot(int)
    def update_difficulty_setting(self, index):
        difficulty = self.view.difficulty_combo.itemText(index)
        self.model.set_setting('difficulty', difficulty)

    def exit_full_screen(self):
        self.logger.debug("Exit full screen")
        resize_and_show_normal(self.view)

    def load_settings(self):
        self.view.sound_checkbox.setChecked(self.model.get_setting('sound'))
        current_difficulty = self.model.get_setting('difficulty')
        index = self.view.difficulty_combo.findText(current_difficulty)
        self.view.difficulty_combo.setCurrentIndex(index)
