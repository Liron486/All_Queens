from PyQt5.QtCore import pyqtSignal, QObject
from models.settings_model import SettingsModel
from models.player import Player, HumanPlayer, AiPlayerEasy, get_available_cells_to_move, check_if_move_wins
from logger import get_logger
from utils import PieceType, PlayerType, WHITE_PIECE_PATH, BLACK_PIECE_PATH

class GameState(QObject):
    piece_was_chosen = pyqtSignal(tuple, list, list)
    player_finish_move = pyqtSignal(dict, list, PlayerType)

    def __init__(self, settings: SettingsModel):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        self.init_game_state(settings)

    def init_game_state(self, settings: SettingsModel):
        self.init_players_settings(settings)
        self.board_size = settings.get_setting('board_size')
        self.sound = settings.get_setting('sound')
        self.difficulty = settings.get_setting('difficulty')
        self.is_edit_mode = settings.get_setting('is_edit_mode')
        self.game_number = 0
        self.moves_to_undo = 0
        self.current_player_index = 0
        self.available_cells = []
        self.cells_in_route = []
        self.game_moves = []
        self.move_in_progress = False
        self.game_in_progress = True
        self.start_new_game(True)

    def init_players_settings(self, settings: SettingsModel):
        names = settings.get_setting('names')
        num_real_players = settings.get_setting('num_real_players')
        is_starting = settings.get_setting('is_starting')
        difficulties = settings.get_setting('difficulty')
        pic_pathes = [WHITE_PIECE_PATH, BLACK_PIECE_PATH]
        piece_types = [PieceType.WHITE, PieceType.BLACK]

        player_types = [PlayerType.HUMAN if i < num_real_players else PlayerType.AI for i in range(len(names))]
        
        if num_real_players == 1:
            difficulties[1] = difficulties[0]
            if not is_starting:
                names[0], names[1] = names[1], names[0]
                player_types[0], player_types[1] = player_types[1], player_types[0]

        self.players = [
            HumanPlayer(name, player_type, difficulty, piece_type, path) if player_type == PlayerType.HUMAN
            else AiPlayerEasy(name, player_type, difficulty, piece_type, path) if player_type == PlayerType.AI and difficulty == "Easy"
            else Player(name, player_type, difficulty, piece_type, path)
            for idx, (name, player_type, difficulty, piece_type, path) in enumerate(zip(names, player_types, difficulties, piece_types, pic_pathes))
        ]

    def init_board(self):
        size = self.board_size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        mid = size // 2

        for i in range(size):
            for j in range(size):
                if i == 0:
                    piece_type = PieceType.BLACK if j % 2 == 0 else PieceType.WHITE
                    self.board[i][j] = piece_type
                    self.players[piece_type.value].init_positions((i,j)) 
                elif i == mid and j == 0:
                    self.board[i][j] = PieceType.BLACK
                    self.players[PieceType.BLACK.value].init_positions((i,j)) 
                elif i == mid and j == size - 1:
                    self.board[i][j] = PieceType.WHITE
                    self.players[PieceType.WHITE.value].init_positions((i,j)) 
                elif i == size - 1:
                    piece_type = PieceType.WHITE if j % 2 == 0 else PieceType.BLACK
                    self.board[i][j] = piece_type
                    self.players[piece_type.value].init_positions((i,j))
                else:
                    self.board[i][j] = PieceType.EMPTY

    def check_move(self, row, col):
        player = self.players[self.current_player_index]
        if row == -1 and col == -1:
            self.reset_player_move(player)
            return

        player_piece_type = player.get_piece_type()
        cell_piece_type = self.board[row][col]
        is_first_click = not player.is_from_assigned()

        if is_first_click:
            if cell_piece_type is player_piece_type:
                self.handle_player_first_move(row, col, player, player_piece_type)
        else:
            if cell_piece_type is PieceType.EMPTY:
                is_valid_cell = (row, col) in self.available_cells
                if is_valid_cell:
                    self.handle_player_second_move(row, col, player, player_piece_type)
                else:
                    self.reset_player_move(player)
            elif cell_piece_type is player_piece_type:
                self.handle_player_first_move(row, col, player, player_piece_type)
            else:
                self.reset_player_move(player)
            
    def check_for_winner(self, last_move):
        row, col = last_move['to'][0], last_move['to'][1]
        piece_type = self.board[row][col]
        is_winner = check_if_move_wins(self.board, row, col, piece_type, self.board_size)
        if is_winner:
            self.game_in_progress = False
        return is_winner

    def __apply_move(self, move, player, is_undo=False):
        self.board[move["to"][0]][move["to"][1]] = self.board[move["from"][0]][move["from"][1]]
        self.board[move["from"][0]][move["from"][1]] = PieceType.EMPTY   
        self.current_player_index = 1 - self.current_player_index
        cells_to_reset = self.available_cells + self.cells_in_route
        player.update_move_number(not is_undo)
        player.reset_move()
        if is_undo:
            self.update_move_route(self.game_moves[-1] if self.game_moves else None)
        else:
            self.update_move_route(move)
        return cells_to_reset

    def get_ai_move(self):
        player = self.players[self.current_player_index]
        other_player = self.players[1 - self.current_player_index]
        move = player.make_move(self.board, other_player.get_positions(), self.board_size)
        cells_to_reset = self.__apply_move(move, player)
        self.game_moves.append(move)
        return move, cells_to_reset

    def handle_player_second_move(self, row, col, player, player_piece_type):
        player.set_to_move(row, col)
        move = player.make_move()
        cells_to_reset = self.__apply_move(move, player)
        self.game_moves.append(move)
        self.player_finish_move.emit(move, cells_to_reset, player.get_player_type())

    def undo_last_move(self):
        self.moves_to_undo -=1
        if self.game_moves:
            last_move = self.game_moves.pop()
            last_move["time_to_wait"] = 1
            last_move["from"], last_move["to"] = last_move["to"], last_move["from"]
            player = self.players[1 - self.current_player_index]
            player.set_from_move(last_move["from"][0], last_move["from"][1])
            player.set_to_move(last_move["to"][0], last_move["to"][1])
            cells_to_reset = self.__apply_move(last_move, player, True)
            return last_move, cells_to_reset
        return None, None

    def player_wants_to_undo_last_move(self):
        self.moves_to_undo += 1
        self.game_in_progress = True
        if not self.move_in_progress:
            move, cells_to_reset = self.undo_last_move()
            self.reset_player_move(self.players[self.current_player_index])
            if move:
                self.logger.debug(f"Undoing Move - {move['to']} to {move['from']}")
                self.player_finish_move.emit(move, cells_to_reset, PlayerType.AI)
                
    def handle_player_first_move(self, row, col, player, player_piece_type):
        player.set_from_move(row, col)
        available_cells = get_available_cells_to_move(self.board, row, col, self.board_size)
        self.piece_was_chosen.emit((row, col), self.available_cells, available_cells)
        self.available_cells = available_cells + [(row, col)]

    def reset_player_move(self, player):
        self.piece_was_chosen.emit((), self.available_cells, [])
        player.reset_move()
        self.available_cells = []
    
    def start_new_game(self, first_game=False):
        self.update_players_data(first_game)
        self.init_board()
        self.current_player_index = 0
        self.game_number += 1
        self.game_in_progress = True
        self.cells_in_route.clear()
        self.game_moves.clear()

    def is_game_in_progress(self):
        return self.game_in_progress

    def get_players(self):
        return self.players

    def get_board(self):
        return self.board

    def get_game_number(self):
        return self.game_number

    def update_score(self, player_name):
        if player_name in self.player_scores:
            self.player_scores[player_name] += 1

    def increment_game_number(self):
        self.game_number += 1

    def get_currrent_player_type(self):
        return self.players[self.current_player_index].get_player_type()

    def get_next_player_name(self):
        return self.players[1 - self.current_player_index].get_name()

    def get_current_player_name(self):
        return self.players[self.current_player_index].get_name()

    def get_route_of_last_move(self):
        return self.cells_in_route

    def is_initial_setup(self):
        return len(self.game_moves) == 0

    def update_players_data(self, first_game):
        if not first_game:
            self.players[1 - self.current_player_index].update_score()
        for player in self.players:
            player.reset_move_number()
            player.clear_positions()

    def update_move_route(self, move):
        self.cells_in_route.clear()
        if move:
            self.cells_in_route.append(move["from"])
            self.cells_in_route.append(move["to"])

    def get_all_cells_in_route(self, move):
        cells = []
        start_row, start_col = move['from']
        end_row, end_col = move['to']

        if start_row == end_row:  # Horizontal move
            step = 1 if start_col < end_col else -1
            for col in range(start_col, end_col + step, step):
                cells.append((start_row, col))
        elif start_col == end_col:  # Vertical move
            step = 1 if start_row < end_row else -1
            for row in range(start_row, end_row + step, step):
                cells.append((row, start_col))
        elif abs(start_row - end_row) == abs(start_col - end_col):  # Diagonal move
            row_step = 1 if start_row < end_row else -1
            col_step = 1 if start_col < end_col else -1
            row, col = start_row, start_col
            while row != end_row + row_step and col != end_col + col_step:
                cells.append((row, col))
                row += row_step
                col += col_step
        return cells



