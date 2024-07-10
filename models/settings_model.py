class SettingsModel:
    def __init__(self):
        self.settings = {
            'sound': True,
            'difficulty': 'Medium',
            'num_real_players': 1,
            'is_starting': True,
            'names' : [
                "player1",
                "player2"
            ]
        }

    def get_setting(self, key):
        return self.settings.get(key, None)

    def set_setting(self, key, value):
        self.settings[key] = value