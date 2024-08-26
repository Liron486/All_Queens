from PyQt5.QtCore import pyqtSignal, QObject
from models.settings_model import SettingsModel
from models.player import Player, HumanPlayer, AiPlayerEasy, get_available_cells_to_move, check_if_move_wins
from logger import get_logger
from utils import PieceType, PlayerType, WHITE_PIECE_PATH, BLACK_PIECE_PATH

class GameState(QObject):
    """
    The GameState class manages the entire state of a game session, including the board,
    players, moves, and the game's overall progress. It interacts with various components
    such as the players and board, and it emits signals to update the UI or other components
    based on player actions and game events.

    Attributes:
        piece_was_chosen_signal (pyqtSignal): Signal emitted when a piece is chosen, carrying the piece's coordinates, available cells to move, and the route of the piece.
        player_finish_move_signal (pyqtSignal): Signal emitted when a player finishes a move, carrying the move details, the player's type, and whether it was an undo operation.
        invalid_move_signal (pyqtSignal): Signal emitted when an invalid move is made.
    """

    piece_was_chosen_signal = pyqtSignal(tuple, list, list)
    player_finish_move_signal = pyqtSignal(dict, PlayerType, bool)
    invalid_move_signal = pyqtSignal()

    def __init__(self, settings: SettingsModel):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        self._init_game_state(settings)

    def _init_game_state(self, settings: SettingsModel):
        """
        Initializes the game state with the provided settings.

        Args:
            settings (SettingsModel): The settings for the game.
        """
        self._init_players_settings(settings)
        self.board_size = settings.get_setting('board_size')
        self.sound = settings.get_setting('sound')
        self.difficulty = settings.get_setting('difficulty')
        self.is_edit_mode = settings.get_setting('is_edit_mode')
        self.game_number = 0
        self.current_player_index = 0
        self.available_cells = []
        self.cells_in_route = []
        self.game_moves = []
        self.game_in_progress = True
        self.found_winner = False
        self.abort_last_move = 0
        self.start_new_game(True)

    def check_move(self, row, col):
        """
        Checks the validity of a move made by the player and handles it accordingly.

        Args:
            row (int): The row index of the move.
            col (int): The column index of the move.
        """
        player = self.players[self.current_player_index]
        if row == -1 and col == -1:
            self._reset_player_move(player)
            return

        player_piece_type = player.get_piece_type()
        cell_piece_type = self.board[row][col]
        is_first_click = not player.is_from_assigned()

        if is_first_click:
            if cell_piece_type is player_piece_type:
                self._handle_player_first_move(row, col, player, player_piece_type)
            else:
                self.invalid_move_signal.emit()
        else:
            if cell_piece_type is PieceType.EMPTY:
                is_valid_cell = (row, col) in self.available_cells
                if is_valid_cell:
                    self._handle_player_second_move(row, col, player, player_piece_type)
                else:
                    self._reset_player_move(player)
                    self.invalid_move_signal.emit()
            elif cell_piece_type is player_piece_type:
                self._handle_player_first_move(row, col, player, player_piece_type)
            else:
                self._reset_player_move(player)
                self.invalid_move_signal.emit()

    def pause_game(self):
        """
        Toggles the game's pause state.

        Returns:
            bool: The new pause state of the game.
        """
        self.game_in_progress = not self.game_in_progress
        player = self.players[self.current_player_index]
        if player.player_type == PlayerType.AI and not self.game_in_progress and not self.found_winner:
            self.abort_last_move += 1
        return not self.game_in_progress

    def check_for_winner(self, last_move):
        """
        Checks if the last move resulted in a win.

        Args:
            last_move (dict): The last move made.

        Returns:
            bool: True if there is a winner, False otherwise.
        """
        row, col = last_move['to'][0], last_move['to'][1]
        piece_type = self.board[row][col]
        is_winner = check_if_move_wins(self.board, row, col, piece_type, self.board_size)
        if is_winner:
            self.found_winner = True
        return is_winner

    def apply_move(self, move, is_undo=False):
        """
        Applies a move to the game board.

        Args:
            move (dict): The move to be applied.
            is_undo (bool): Whether the move is an undo operation.

        Returns:
            list: The cells that need to be reset after the move.
        """
        self.found_winner = False
        self.board[move["to"][0]][move["to"][1]] = self.board[move["from"][0]][move["from"][1]]
        self.board[move["from"][0]][move["from"][1]] = PieceType.EMPTY   
        cells_to_reset = self.available_cells + self.cells_in_route

        if is_undo:
            player = self.players[1 - self.current_player_index]
            self._update_move_route(self.game_moves[-1] if self.game_moves else None)
        else:
            player = self.players[self.current_player_index]
            self._update_move_route(move)
            self.game_moves.append(move)

        self.current_player_index = 1 - self.current_player_index
        player.update_move_number(not is_undo)
        player.reset_move()
        return cells_to_reset

    def get_ai_move(self):
        """
        Gets the next move from the AI player.

        Returns:
            dict: The move made by the AI.
        """
        player = self.players[self.current_player_index]
        other_player = self.players[1 - self.current_player_index]
        move = player.make_move(self.board, other_player.get_positions(), self.board_size)
        return move

    def player_wants_to_undo_last_move(self):
        """
        Handles the player's request to undo the last move.
        """
        move = self._undo_last_move()
        self.piece_was_chosen_signal.emit((), self.available_cells, [])
        self.available_cells = []
        if move:
            self.logger.debug(f"Undoing Move - {move['to']} to {move['from']}")
            self.player_finish_move_signal.emit(move, PlayerType.AI, True)

    def start_new_game(self, first_game=False):
        """
        Starts a new game, resetting all necessary states.

        Args:
            first_game (bool): Whether this is the first game being started.
        """
        self._update_players_data(first_game)
        self._init_board()
        self.current_player_index = 0
        self.game_number += 1
        self.found_winner = False
        self.cells_in_route.clear()
        self.game_moves.clear()

    def is_game_in_progress(self):
        """
        Checks if the game is currently in progress.

        Returns:
            bool: True if the game is in progress, False otherwise.
        """
        return self.game_in_progress

    def is_winner_found(self):
        """
        Checks if a winner has been found.

        Returns:
            bool: True if a winner is found, False otherwise.
        """
        return self.found_winner

    def get_players(self):
        """
        Gets the list of players.

        Returns:
            list: The players in the game.
        """
        return self.players

    def get_board(self):
        """
        Gets the current state of the game board.

        Returns:
            list: The game board.
        """
        return self.board

    def get_game_number(self):
        """
        Gets the current game number.

        Returns:
            int: The current game number.
        """
        return self.game_number

    def update_score(self, player_name):
        """
        Updates the score for a specific player.

        Args:
            player_name (str): The name of the player whose score is being updated.
        """
        if player_name in self.player_scores:
            self.player_scores[player_name] += 1

    def increment_game_number(self):
        """
        Increments the game number.
        """
        self.game_number += 1

    def get_current_player_type(self):
        """
        Gets the current player's type.

        Returns:
            PlayerType: The current player's type.
        """
        return self.players[self.current_player_index].get_player_type()

    def get_next_player_name(self):
        """
        Gets the name of the next player.

        Returns:
            str: The name of the next player.
        """
        return self.players[1 - self.current_player_index].get_name()

    def get_current_player_name(self):
        """
        Gets the name of the current player.

        Returns:
            str: The name of the current player.
        """
        return self.players[self.current_player_index].get_name()

    def get_route_of_last_move(self):
        """
        Gets the route of the last move made.

        Returns:
            list: The cells involved in the last move.
        """
        return self.cells_in_route

    def is_initial_setup(self):
        """
        Checks if the game is still in its initial setup phase.

        Returns:
            bool: True if the game is in its initial setup, False otherwise.
        """
        return len(self.game_moves) == 0

    def abort_move(self):
        """
        Decreases the abort move counter.
        """
        self.abort_last_move -= 1

    def is_need_to_abort_move(self):
        """
        Checks if the current move needs to be aborted.

        Returns:
            bool: True if the move should be aborted, False otherwise.
        """
        return self.abort_last_move > 0


    def get_all_cells_in_route(self, move):
        """
        Gets all the cells in the route of the specified move.

        Args:
            move (dict): The move to calculate the route for.

        Returns:
            list: The cells in the route of the move.
        """
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

    def _init_players_settings(self, settings: SettingsModel):
        """
        Initializes the players based on the settings provided.

        Args:
            settings (SettingsModel): The settings for the players.
        """
        names = settings.get_setting('names')
        num_real_players = settings.get_setting('num_real_players')
        is_starting = settings.get_setting('is_starting')
        difficulties = settings.get_setting('difficulty')
        pic_paths = [WHITE_PIECE_PATH, BLACK_PIECE_PATH]
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
            for idx, (name, player_type, difficulty, piece_type, path) in enumerate(zip(names, player_types, difficulties, piece_types, pic_paths))
        ]

    def _init_board(self):
        """
        Initializes the game board with initial positions of pieces.
        """
        size = self.board_size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        middle_index = size // 2

        for i in range(size):
            for j in range(size):
                if i == 0:
                    piece_type = PieceType.BLACK if j % 2 == 0 else PieceType.WHITE
                    self.board[i][j] = piece_type
                    self.players[piece_type.value].init_positions((i, j)) 
                elif i == middle_index and j == 0:
                    self.board[i][j] = PieceType.BLACK
                    self.players[PieceType.BLACK.value].init_positions((i, j)) 
                elif i == middle_index and j == size - 1:
                    self.board[i][j] = PieceType.WHITE
                    self.players[PieceType.WHITE.value].init_positions((i, j)) 
                elif i == size - 1:
                    piece_type = PieceType.WHITE if j % 2 == 0 else PieceType.BLACK
                    self.board[i][j] = piece_type
                    self.players[piece_type.value].init_positions((i, j))
                else:
                    self.board[i][j] = PieceType.EMPTY

    def _handle_player_second_move(self, row, col, player, player_piece_type):
        """
        Handles the player's second move.

        Args:
            row (int): The row index of the move.
            col (int): The column index of the move.
            player (Player): The player making the move.
            player_piece_type (PieceType): The type of piece the player controls.
        """
        player.set_to_move(row, col)
        move = player.make_move()
        self.player_finish_move_signal.emit(move, player.get_player_type(), False)

    def _undo_last_move(self):
        """
        Undoes the last move made in the game.

        Returns:
            dict: The last move that was undone, or None if no moves to undo.
        """
        if self.game_moves:
            last_move = self.game_moves.pop()
            last_move["waiting_time"] = 0
            last_move["from"], last_move["to"] = last_move["to"], last_move["from"]
            current_player = self.players[self.current_player_index]
            if current_player.player_type == PlayerType.AI and not self.found_winner and self.game_in_progress:
                self.abort_last_move += 1
            if self.found_winner:
                self.found_winner = False
            player = self.players[1 - self.current_player_index]
            player.set_from_move(last_move["from"][0], last_move["from"][1])
            player.set_to_move(last_move["to"][0], last_move["to"][1])
            return last_move
        return None

    def _handle_player_first_move(self, row, col, player, player_piece_type):
        """
        Handles the player's first move.

        Args:
            row (int): The row index of the move.
            col (int): The column index of the move.
            player (Player): The player making the move.
            player_piece_type (PieceType): The type of piece the player controls.
        """
        player.set_from_move(row, col)
        available_cells = get_available_cells_to_move(self.board, row, col, self.board_size)
        self.piece_was_chosen_signal.emit((row, col), self.available_cells, available_cells)
        self.available_cells = available_cells + [(row, col)]

    def _reset_player_move(self, player):
        """
        Resets the player's current move.

        Args:
            player (Player): The player whose move is being reset.
        """
        self.piece_was_chosen_signal.emit((), self.available_cells, [])
        player.reset_move()
        self.available_cells = []

    def _update_players_data(self, first_game):
        """
        Updates the players data at the start of a new game.

        Args:
            first_game (bool): Whether this is the first game being started.
        """
        if not first_game:
            self.players[1 - self.current_player_index].update_score()
        for player in self.players:
            player.reset_move_number()
            player.clear_positions()

    def _update_move_route(self, move):
        """
        Updates the route of the last move.

        Args:
            move (dict): The move to update the route for.
        """
        self.cells_in_route.clear()
        if move:
            self.cells_in_route.append(move["from"])
            self.cells_in_route.append(move["to"])