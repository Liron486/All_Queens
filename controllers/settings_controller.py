from models.settings_model import SettingsModel
from views.settings_view import SettingsWindow
from PyQt5.QtCore import pyqtSlot

class SettingsController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.escapePressed.connect(self.exit_full_screen)

    @pyqtSlot(int)
    def update_difficulty_setting(self, index):
        difficulty = self.view.difficulty_combo.itemText(index)
        self.model.set_setting('difficulty', difficulty)

    def exit_full_screen(self):
        self.view.showNormal()

    def load_settings(self):
        self.view.sound_checkbox.setChecked(self.model.get_setting('sound'))
        current_difficulty = self.model.get_setting('difficulty')
        index = self.view.difficulty_combo.findText(current_difficulty)
        self.view.difficulty_combo.setCurrentIndex(index)
