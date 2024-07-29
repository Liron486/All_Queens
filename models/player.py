from PyQt5.QtCore import pyqtSignal
from utils import PieceType

def get_available_cells_in_direction(board, row, col, row_step, col_step, max_size):
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
    consecutive_row = 1
    consecutive_col = 1
    consecutive_diag = 1
    consecutive_anti_diag = 1

    # Check horizontal
    consecutive_row += check_consecutive_pieces_in_direction(board, row, col, piece_type, 0, 1, max_size)  # Right
    consecutive_row += check_consecutive_pieces_in_direction(board, row, col, piece_type, 0, -1, max_size)  # Left
    if consecutive_row >= 4:
        return True

    # Check vertical
    consecutive_col += check_consecutive_pieces_in_direction(board, row, col, piece_type, 1, 0, max_size)  # Down
    consecutive_col += check_consecutive_pieces_in_direction(board, row, col, piece_type, -1, 0, max_size)  # Up
    if consecutive_col >= 4:
        return True

    # Check diagonal (top-left to bottom-right)
    consecutive_diag += check_consecutive_pieces_in_direction(board, row, col, piece_type, -1, 1, max_size)  # Top-right
    consecutive_diag += check_consecutive_pieces_in_direction(board, row, col, piece_type, 1, -1, max_size)  # Bottom-left
    if consecutive_diag >= 4:
        return True

    # Check anti-diagonal (top-right to bottom-left)
    consecutive_anti_diag += check_consecutive_pieces_in_direction(board, row, col, piece_type, -1, -1, max_size)  # Top-left
    consecutive_anti_diag += check_consecutive_pieces_in_direction(board, row, col, piece_type, 1, 1, max_size)  # Bottom-right
    if consecutive_anti_diag >= 4:
        return True

    return False

def get_available_cells_to_move(board, row, col, max_size):
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
    def __init__(self, name, player_type, difficulty, piece_type, piece_path):
        self.name = name
        self.player_type = player_type
        self.difficulty = difficulty
        self.piece_type = piece_type
        self.piece_path = piece_path
        self.score = 0

    def make_move(self, *args, **kwargs):
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

    def update_score(self):
        self.score += 1

class HumanPlayer(Player):
    def __init__(self, name, player_type, difficulty, piece_type, piece_path):
        super().__init__(name, player_type, difficulty, piece_type, piece_path)
        self.move = { "from": None, "to": None, "waiting_time": 0}
    
    def make_move(self):
        return self.move

    def reset_move(self):
        self.move["from"] = None
        self.move["to"] = None

    def is_from_assigned(self):
        return self.move["from"] is not None

    def set_from_move(self, row, col):
        self.move["from"] = (row, col)
    
    def set_to_move(self, row, col):
        self.move["to"] = (row, col)

