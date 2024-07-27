from models.settings_model import SettingsModel
from logger import get_logger
from utils import PieceType

class GameState:
    def __init__(self, settings: SettingsModel):
        self.logger = get_logger(self.__class__.__name__)
        self.init_game_state(settings)

    def init_game_state(self, settings: SettingsModel):
        self.init_players_settings(settings)
        self.board_size = settings.get_setting('board_size')
        self.sound = settings.get_setting('sound')
        self.difficulty = settings.get_setting('difficulty')
        self.is_edit_mode = settings.get_setting('is_edit_mode')
        self.game_number = 1
        self.init_board()

    def init_players_settings(self, settings: SettingsModel):
        names = settings.get_setting('names')
        num_real_players = settings.get_setting('num_real_players')
        is_starting = settings.get_setting('is_starting')
        difficulties = settings.get_setting('difficulty')

        player_types = ['Human' if i < num_real_players else 'AI' for i in range(len(names))]
        
        if num_real_players == 1:
            difficulties[1] = difficulties[0]
            if not is_starting:
                names[0], names[1] = names[1], names[0]
                player_types[0], player_types[1] = player_types[1], player_types[0]

        self.players = {
            name: {'score': 0, 'type': player_type, 'difficulty': difficulty}
            for name, player_type, difficulty in zip(names, player_types, difficulties)
        }

    def init_board(self):
        size = self.board_size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        mid = size // 2

        for i in range(size):
            for j in range(size):
                if i == 0:
                    self.board[i][j] = PieceType.BLACK if j % 2 == 0 else PieceType.WHITE
                elif i == mid and j == 0:
                    self.board[i][j] = PieceType.BLACK
                elif i == mid and j == size - 1:
                    self.board[i][j] = PieceType.WHITE
                elif i == size - 1:
                    self.board[i][j] = PieceType.WHITE if j % 2 == 0 else PieceType.BLACK
                else:
                    self.board[i][j] = PieceType.EMPTY

    def get_player_names(self):
        return self.names

    def get_player_scores(self):
        return self.player_scores

    def get_player_types(self):
        return self.player_types

    def get_game_number(self):
        return self.game_number

    def get_board(self):
        return self.board

    def update_score(self, player_name):
        if player_name in self.player_scores:
            self.player_scores[player_name] += 1

    def increment_game_number(self):
        self.game_number += 1

