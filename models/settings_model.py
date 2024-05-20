class SettingsModel:
    def __init__(self):
        self.settings = {
            'sound': True,
            'difficulty': 'Medium'
        }

    def get_setting(self, key):
        return self.settings.get(key, None)

    def set_setting(self, key, value):
        self.settings[key] = value