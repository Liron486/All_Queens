class SettingsModel:
    """
    A class to manage game settings.
    """
    
    def __init__(self):
        """
        Initializes the SettingsModel with default settings.
        """
        self.settings = {
            'board_size': 5,
            'difficulty': ['Easy', 'Easy'],
            'num_real_players': 1,
            'is_starting': True,
            'names': ["player1", "player2"],
            'is_edit_mode': False
        }
    
    def get_setting(self, key):
        """
        Retrieves the value of a specific setting.

        Args:
            key (str): The setting key.

        Returns:
            The value associated with the key, or None if the key is not found.
        """
        return self.settings.get(key, None)
    
    def set_setting(self, key, value):
        """
        Sets the value for a specific setting.

        Args:
            key (str): The setting key.
            value: The value to set for the key.
        """
        self.settings[key] = value
