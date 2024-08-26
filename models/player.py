from PyQt5.QtCore import pyqtSignal
from utils import PieceType
import copy
import random

WIN_CONDITION = 4

def get_available_cells_in_direction(board, row, col, row_step, col_step, max_size):
    """
    Returns a list of available cells in the specified direction until a non-empty cell is encountered.

    Args:
        board (list): The game board.
        row (int): The starting row index.
        col (int): The starting column index.
        row_step (int): The row step to move in the direction.
        col_step (int): The column step to move in the direction.
        max_size (int): The maximum size of the board.

    Returns:
        list: A list of available cells in the specified direction.
    """
    available_cells = []
    i, j = row + row_step, col + col_step
    while 0 <= i < max_size and 0 <= j < max_size:
        if board[i][j] is PieceType.EMPTY:
            available_cells.append((i, j))
            i += row_step
            j += col_step
        else:
            break
    return available_cells

def check_consecutive_pieces_in_direction(board, row, col, piece_type, row_step, col_step, max_size):
    """
    Counts consecutive pieces in the specified direction.

    Args:
        board (list): The game board.
        row (int): The starting row index.
        col (int): The starting column index.
        piece_type (PieceType): The type of the piece to count.
        row_step (int): The row step to move in the direction.
        col_step (int): The column step to move in the direction.
        max_size (int): The maximum size of the board.

    Returns:
        int: The number of consecutive pieces in the specified direction.
    """
    consecutive_pieces = 0
    i, j = row + row_step, col + col_step
    while 0 <= i < max_size and 0 <= j < max_size:
        if board[i][j] is piece_type:
            consecutive_pieces += 1
            i += row_step
            j += col_step
        else:
            break
    return consecutive_pieces

def check_if_move_wins(board, row, col, piece_type, max_size):
    """
    Checks if the current move results in a win.

    Args:
        board (list): The game board.
        row (int): The row index of the move.
        col (int): The column index of the move.
        piece_type (PieceType): The type of the piece being moved.
        max_size (int): The maximum size of the board.

    Returns:
        bool: True if the move results in a win, False otherwise.
    """
    consecutive_row = 1
    consecutive_col = 1
    consecutive_diag = 1
    consecutive_anti_diag = 1

    # Check horizontal
    consecutive_row += check_consecutive_pieces_in_direction(board, row, col, piece_type, 0, 1, max_size)  # Right
    consecutive_row += check_consecutive_pieces_in_direction(board, row, col, piece_type, 0, -1, max_size)  # Left
    if consecutive_row >= WIN_CONDITION:
        return True

    # Check vertical
    consecutive_col += check_consecutive_pieces_in_direction(board, row, col, piece_type, 1, 0, max_size)  # Down
    consecutive_col += check_consecutive_pieces_in_direction(board, row, col, piece_type, -1, 0, max_size)  # Up
    if consecutive_col >= WIN_CONDITION:
        return True

    # Check diagonal (top-left to bottom-right)
    consecutive_diag += check_consecutive_pieces_in_direction(board, row, col, piece_type, -1, 1, max_size)  # Top-right
    consecutive_diag += check_consecutive_pieces_in_direction(board, row, col, piece_type, 1, -1, max_size)  # Bottom-left
    if consecutive_diag >= WIN_CONDITION:
        return True

    # Check anti-diagonal (top-right to bottom-left)
    consecutive_anti_diag += check_consecutive_pieces_in_direction(board, row, col, piece_type, -1, -1, max_size)  # Top-left
    consecutive_anti_diag += check_consecutive_pieces_in_direction(board, row, col, piece_type, 1, 1, max_size)  # Bottom-right
    if consecutive_anti_diag >= WIN_CONDITION:
        return True

    return False

def get_available_cells_to_move(board, row, col, max_size):
    """
    Gets all available cells that a piece can move to from a specific position.

    Args:
        board (list): The game board.
        row (int): The row index of the current position.
        col (int): The column index of the current position.
        max_size (int): The maximum size of the board.

    Returns:
        list: A list of available cells where the piece can move.
    """
    available_cells = []

    # Horizontal directions
    available_cells.extend(get_available_cells_in_direction(board, row, col, 0, 1, max_size))  # Right
    available_cells.extend(get_available_cells_in_direction(board, row, col, 0, -1, max_size))  # Left

    # Vertical directions
    available_cells.extend(get_available_cells_in_direction(board, row, col, 1, 0, max_size))  # Down
    available_cells.extend(get_available_cells_in_direction(board, row, col, -1, 0, max_size))  # Up

    # Diagonal directions
    available_cells.extend(get_available_cells_in_direction(board, row, col, -1, 1, max_size))  # Top-right
    available_cells.extend(get_available_cells_in_direction(board, row, col, 1, -1, max_size))  # Bottom-left

    # Anti-diagonal directions
    available_cells.extend(get_available_cells_in_direction(board, row, col, -1, -1, max_size))  # Top-left
    available_cells.extend(get_available_cells_in_direction(board, row, col, 1, 1, max_size))  # Bottom-right

    return available_cells

class Player:
    """
    The Player class represents a generic player in the game, providing common attributes
    and methods that are shared between different types of players (e.g., Human and AI).

    Attributes:
        name (str): The name of the player.
        player_type (PlayerType): The type of the player (Human or AI).
        difficulty (str): The difficulty level if the player is AI.
        piece_type (PieceType): The type of piece the player controls.
        piece_path (str): The path to the image of the piece.
        score (int): The score of the player.
        move_num (int): The number of moves made by the player.
        positions (list): The list of positions occupied by the player's pieces.
        move (dict): The current move details, including from, to, and waiting_time.
    """
    def __init__(self, name, player_type, difficulty, piece_type, piece_path):
        """
        Initializes a Player object.

        Args:
            name (str): The name of the player.
            player_type (PlayerType): The type of the player (Human or AI).
            difficulty (str): The difficulty level if the player is AI.
            piece_type (PieceType): The type of piece the player controls.
            piece_path (str): The path to the image of the piece.
        """
        self.name = name
        self.player_type = player_type
        self.difficulty = difficulty
        self.piece_type = piece_type
        self.piece_path = piece_path
        self.score = 0
        self.move_num = 0
        self.positions = []
        self.move = {"from": None, "to": None, "waiting_time": 0}

    def make_move(self, *args, **kwargs):
        """
        Abstract method to be implemented by subclasses.
        """
        raise NotImplementedError("This method should be implemented by subclasses")

    def get_name(self):
        return self.name
    
    def get_player_type(self):
        return self.player_type

    def get_piece_type(self):
        return self.piece_type

    def get_difficulty(self):
        return self.difficulty

    def get_piece_path(self):
        return self.piece_path

    def get_score(self):
        return self.score

    def get_move_number(self):
        return self.move_num

    def get_positions(self):
        return self.positions

    def init_positions(self, point):
        """
        Initializes the player's positions on the board.

        Args:
            point (tuple): The position to be initialized.
        """
        self.positions.append(point)

    def update_positions(self):
        """
        Updates the player's positions after a move.
        """
        self.positions.remove(self.move['from'])
        self.positions.append(self.move['to'])

    def update_score(self):
        """
        Increments the player's score.
        """
        self.score += 1

    def update_move_number(self, increase=True):
        """
        Updates the player's move number.

        Args:
            increase (bool): Whether to increment or decrement the move number.
        """
        if increase:
            self.move_num += 1
        else:
            self.move_num -= 1

    def reset_move_number(self):
        """
        Resets the player's move number to zero.
        """
        self.move_num = 0

    def clear_positions(self):
        """
        Clears the player's positions on the board.
        """
        self.positions.clear()

    def is_move_assigned(self):
        """
        Checks if a move is fully assigned (both from and to positions).

        Returns:
            bool: True if both from and to positions are assigned, False otherwise.
        """
        return self.move["from"] is not None and self.move["to"] is not None

    def is_from_assigned(self):
        """
        Checks if the 'from' position of the move is assigned.

        Returns:
            bool: True if the 'from' position is assigned, False otherwise.
        """
        return self.move["from"] is not None

    def set_from_move(self, row, col):
        """
        Sets the 'from' position of the move.

        Args:
            row (int): The row index of the 'from' position.
            col (int): The column index of the 'from' position.
        """
        self.move["from"] = (row, col)
    
    def set_to_move(self, row, col):
        """
        Sets the 'to' position of the move.

        Args:
            row (int): The row index of the 'to' position.
            col (int): The column index of the 'to' position.
        """
        self.move["to"] = (row, col)

    def set_move_waiting_time(self, time):
        """
        Sets the waiting time for the move.

        Args:
            time (int): The waiting time for the move.
        """
        self.move["waiting_time"] = time

    def reset_move(self):
        """
        Resets the current move after it is completed.
        """
        if self.is_move_assigned():
            self.update_positions()
            self.move["from"] = None
            self.move["to"] = None

class HumanPlayer(Player):
    """
    The HumanPlayer class represents a human player in the game, inheriting from the Player class.
    """
    def __init__(self, name, player_type, difficulty, piece_type, piece_path):
        """
        Initializes a HumanPlayer object.

        Args:
            name (str): The name of the player.
            player_type (PlayerType): The type of the player (Human).
            difficulty (str): The difficulty level (not used for HumanPlayer).
            piece_type (PieceType): The type of piece the player controls.
            piece_path (str): The path to the image of the piece.
        """
        super().__init__(name, player_type, difficulty, piece_type, piece_path)
    
    def make_move(self):
        """
        Returns a deep copy of the current move.
        
        Returns:
            dict: A deep copy of the move.
        """
        return copy.deepcopy(self.move)

class AiPlayerEasy(Player):
    """
    The AiPlayerEasy class represents an AI player with an "Easy" difficulty level,
    inheriting from the Player class.
    """
    def __init__(self, name, player_type, difficulty, piece_type, piece_path):
        """
        Initializes an AiPlayerEasy object.

        Args:
            name (str): The name of the player.
            player_type (PlayerType): The type of the player (AI).
            difficulty (str): The difficulty level (Easy).
            piece_type (PieceType): The type of piece the player controls.
            piece_path (str): The path to the image of the piece.
        """
        super().__init__(name, player_type, difficulty, piece_type, piece_path)

    def make_move(self, board, other_player_positions, board_size):
        """
        Makes a move for the Easy AI player by selecting a random valid move.

        Args:
            board (list): The game board.
            other_player_positions (list): The positions of the other player's pieces.
            board_size (int): The size of the game board.

        Returns:
            dict: A deep copy of the move made by the AI.
        """
        from_move = None
        to_move = None
        available_moves = None
        while not available_moves:
            piece = random.choice(self.positions)
            available_moves = get_available_cells_to_move(board, piece[0], piece[1], board_size)
            if available_moves:
                to_move = random.choice(available_moves)
                self.set_from_move(piece[0], piece[1])
                self.set_to_move(to_move[0], to_move[1])
        self.move["waiting_time"] = 1
        return copy.deepcopy(self.move)
