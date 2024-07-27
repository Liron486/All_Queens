class SettingsModel:
    def __init__(self):
        self.settings = {
            'board_size': 5,
            'sound': False,
            'difficulty': [
                'Easy',
                'Easy'
            ],
            'num_real_players': 1,
            'is_starting': True,
            'names' : [
                "player1",
                "player2"
            ],
            'is_edit_mode': False
        }

    def get_setting(self, key):
        return self.settings.get(key, None)

    def set_setting(self, key, value):
        self.settings[key] = value