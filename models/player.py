from PyQt5.QtCore import pyqtSignal
from utils import PieceType
import copy
import random

WIN_CONDITION = 4

def get_all_cells_in_route(from_move, to_move):
    """
    Generates a list of all the cells between two coordinates on a grid, 
    including both the start and end coordinates. The function supports 
    horizontal, vertical, and diagonal moves.

    Args:
        from_move (tuple): A tuple (start_row, start_col) representing the starting coordinates.
        to_move (tuple): A tuple (end_row, end_col) representing the ending coordinates.

    Returns:
        list: A list of tuples representing all the cells in the route from 
        `to_move` to `from_move`, in reverse order (i.e., `to_move` is the 
        first element in the list).
    """
    cells = []
    start_row, start_col = from_move
    end_row, end_col = to_move

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

    return cells[::-1]  # Return the cells list in reverse order


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

def check_consecutive_pieces_in_direction(board, row, col, piece_type, max_size, row_step, col_step):
    """
    Checks for consecutive pieces of a given type in a specific direction on the board, 
    starting from the given position and moving according to the provided row and column steps.

    Args:
        board (list): A 2D list representing the game board.
        row (int): The starting row index on the board.
        col (int): The starting column index on the board.
        piece_type (PieceType): The type of the piece to check for (e.g., white or black).
        max_size (int): The size of the board (number of rows/columns).
        row_step (int): The step increment for row movement (e.g., 1 for down, -1 for up, 0 for no row change).
        col_step (int): The step increment for column movement (e.g., 1 for right, -1 for left, 0 for no column change).

    Returns:
        tuple: 
            - int: The number of consecutive pieces of the specified type found in the given direction.
            - list: A list of tuples representing the positions of the consecutive pieces.
    """
    consecutive_pieces = []
    if row_step == 0 and col_step == 0:
        return 0, consecutive_pieces

    i, j = row + row_step, col + col_step
    while 0 <= i < max_size and 0 <= j < max_size:
        if board[i][j] == piece_type:
            consecutive_pieces.append((i, j))  
            i += row_step
            j += col_step
        else:
            break
    return len(consecutive_pieces), consecutive_pieces


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
        tuple: (bool, list) 
               - True and the list of winning positions if the move results in a win.
               - False and an empty list otherwise.
    """
    # Helper function to combine results
    def check_and_collect(direction_func):
        count, positions = direction_func(board, row, col, piece_type, max_size)
        return count, positions

    # Check horizontal
    consecutive_row_right, right_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, 0, 1))
    consecutive_row_left, left_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, 0, -1))
    total_consecutive_row = consecutive_row_right + consecutive_row_left + 1  # Include the current piece
    if total_consecutive_row >= WIN_CONDITION:
        row_positions = right_positions + [(row, col)] + left_positions
        return True, row_positions

    # Check vertical
    consecutive_col_down, down_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, 1, 0))
    consecutive_col_up, up_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, -1, 0))
    total_consecutive_col = consecutive_col_down + consecutive_col_up + 1  # Include the current piece
    if total_consecutive_col >= WIN_CONDITION:
        col_positions = down_positions + [(row, col)] + up_positions
        return True, col_positions

    # Check diagonal (top-left to bottom-right)
    consecutive_diag_top_right, top_right_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, -1, 1))
    consecutive_diag_bottom_left, bottom_left_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, 1, -1))
    total_consecutive_diag = consecutive_diag_top_right + consecutive_diag_bottom_left + 1  # Include the current piece
    if total_consecutive_diag >= WIN_CONDITION:
        diag_positions = top_right_positions + [(row, col)] + bottom_left_positions
        return True, diag_positions

    # Check anti-diagonal (top-right to bottom-left)
    consecutive_anti_diag_top_left, top_left_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, -1, -1))
    consecutive_anti_diag_bottom_right, bottom_right_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, 1, 1))
    total_consecutive_anti_diag = consecutive_anti_diag_top_left + consecutive_anti_diag_bottom_right + 1  # Include the current piece
    if total_consecutive_anti_diag >= WIN_CONDITION:
        anti_diag_positions =  top_left_positions + [(row, col)] + bottom_right_positions
        return True, anti_diag_positions

    return False, []


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
        self._name = name
        self._player_type = player_type
        self._difficulty = difficulty
        self._piece_type = piece_type
        self._piece_path = piece_path
        self._score = 0
        self._move_num = 0
        self._positions = []
        self._move = {"from": None, "to": None, "waiting_time": 0}

    def make_move(self, *args, **kwargs):
        """
        Abstract method to be implemented by subclasses.
        """
        raise NotImplementedError("This method should be implemented by subclasses")

    @property
    def name(self):
        return self._name

    @property
    def player_type(self):
        return self._player_type

    @property
    def piece_type(self):
        return self._piece_type

    @property
    def difficulty(self):
        return self._difficulty

    @property
    def piece_path(self):
        return self._piece_path

    @property
    def score(self):
        return self._score

    @property
    def move_number(self):
        return self._move_num

    @property
    def positions(self):
        return self._positions

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
        self.positions.remove(self._move['from'])
        self.positions.append(self._move['to'])

    def update_score(self):
        """
        Increments the player's score.
        """
        self._score += 1

    def update_move_number(self, increase=True):
        """
        Updates the player's move number.

        Args:
            increase (bool): Whether to increment or decrement the move number.
        """
        if increase:
            self._move_num += 1
        else:
            self._move_num -= 1

    def reset_move_number(self):
        """
        Resets the player's move number to zero.
        """
        self._move_num = 0

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
        return self._move["from"] is not None and self._move["to"] is not None

    def is_from_assigned(self):
        """
        Checks if the 'from' position of the move is assigned.

        Returns:
            bool: True if the 'from' position is assigned, False otherwise.
        """
        return self._move["from"] is not None

    def set_from_move(self, row, col):
        """
        Sets the 'from' position of the move.

        Args:
            row (int): The row index of the 'from' position.
            col (int): The column index of the 'from' position.
        """
        self._move["from"] = (row, col)
    
    def set_to_move(self, row, col):
        """
        Sets the 'to' position of the move.

        Args:
            row (int): The row index of the 'to' position.
            col (int): The column index of the 'to' position.
        """
        self._move["to"] = (row, col)

    def set_move_waiting_time(self, time):
        """
        Sets the waiting time for the move.

        Args:
            time (int): The waiting time for the move.
        """
        self._move["waiting_time"] = time

    def reset_move(self):
        """
        Resets the current move after it is completed.
        """
        if self.is_move_assigned():
            self.update_positions()
            self._move["from"] = None
            self._move["to"] = None

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
        return copy.deepcopy(self._move)

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
        available_moves = None
        while not available_moves:
            piece = random.choice(self.positions)
            available_moves = get_available_cells_to_move(board, piece[0], piece[1], board_size)
            if available_moves:
                to_move = random.choice(available_moves)
                self.set_from_move(piece[0], piece[1])
                self.set_to_move(to_move[0], to_move[1])
        self._move["waiting_time"] = 1
        return copy.deepcopy(self._move)

class AiPlayerMedium(Player):
    def __init__(self, name, player_type, difficulty, piece_type, piece_path):
        super().__init__(name, player_type, difficulty, piece_type, piece_path)

    def make_move(self, board, other_player_positions, board_size):
        """
        Determines and executes the next move for the player. 
        The move can be a winning move, a blocking move, or a random move based on available options.

        Args:
            board (list): The current state of the game board.
            other_player_positions (list): Positions of the opponent's pieces.
            board_size (int): The size of the board.

        Returns:
            dict: A deep copy of the player's move, including the waiting time.
        """
        found_move = None

        # Check if the player can win in a single move
        found_move = self._attempt_winning_move(board, self.positions, self.piece_type, board_size)

        # Check if the opponent can win and block if necessary
        if not found_move:
            other_player_type = PieceType.WHITE if self.piece_type == PieceType.BLACK else PieceType.BLACK
            found_move = self._attempt_blocking_move(board, other_player_positions, other_player_type, board_size)

        # If no critical moves found, make a random move
        if not found_move:
            found_move = self._make_random_move(board, other_player_positions, board_size)

        self._move["waiting_time"] = 1
        return copy.deepcopy(self._move)

    def _attempt_winning_move(self, board, positions, piece_type, board_size):
        """
        Attempts to find and execute a winning move for the player.

        Args:
            board (list): The current state of the game board.
            positions (list): Current positions of the player's pieces.
            piece_type (PieceType): The type of the player's pieces.
            board_size (int): The size of the board.

        Returns:
            bool: True if a winning move was found and executed, False otherwise.
        """
        from_move, to_move = self._find_winner_move(board, positions, piece_type, board_size)
        if from_move:
            self._set_move(from_move, to_move)
            return True
        return False

    def _attempt_blocking_move(self, board, other_player_positions, other_player_type, board_size):
        """
        Attempts to block the opponent's winning move.

        Args:
            board (list): The current state of the game board.
            other_player_positions (list): Positions of the opponent's pieces.
            other_player_type (PieceType): The type of the opponent's pieces.
            board_size (int): The size of the board.

        Returns:
            bool: True if a blocking move was found and executed, False otherwise.
        """
        from_move, to_move = self._find_winner_move(board, other_player_positions, other_player_type, board_size)
        if from_move:
            from_move, to_move = self._try_to_block_move(board, from_move, to_move, board_size)
            if from_move:
                self._set_move(from_move, to_move)
                return True
        return False

    def _make_random_move(self, board, other_player_positions, board_size):
        """
        Makes a random move for the player that avoids allowing the opponent to win. 
        The function selects a random piece and tries a random valid move, ensuring 
        the move does not lead to an immediate win for the opponent.

        Args:
            board (list): The current state of the game board.
            other_player_positions (list): Positions of the opponent's pieces.
            board_size (int): The size of the board.
        """
        other_player_type = PieceType.WHITE if self.piece_type == PieceType.BLACK else PieceType.BLACK
        found_move = None
        while not found_move:
            piece = random.choice(self.positions)
            available_moves = get_available_cells_to_move(board, piece[0], piece[1], board_size)
            if available_moves:
                to_move = random.choice(available_moves)
                is_opponent_will_win, _ = check_if_move_wins(board, piece[0], piece[1], other_player_type, board_size)
                if not is_opponent_will_win:
                    self._set_move(piece, to_move)
                    found_move = True
                else:
                    available_moves.remove(to_move)

    def _set_move(self, from_move, to_move):
        """
        Sets the move's from and to positions.

        Args:
            from_move (tuple): The initial position of the piece.
            to_move (tuple): The target position of the piece.
        """
        self.set_from_move(from_move[0], from_move[1])
        self.set_to_move(to_move[0], to_move[1])


    def _try_to_block_move(self, board, from_move, to_move, board_size):
        """
        Attempts to block the opponent's move by placing a piece in the path of the opponent's 
        potential winning move.

        Args:
            board (list): The current state of the game board.
            from_move (tuple): The initial position of the opponent's piece.
            to_move (tuple): The target position of the opponent's piece.
            board_size (int): The size of the board.

        Returns:
            tuple: The blocking piece and its new position, or (None, None) if no block is found.
        """
        cells = get_all_cells_in_route(from_move, to_move)
        for cell in cells:
            for piece in self.positions:
                available_moves = get_available_cells_to_move(board, piece[0], piece[1], board_size)
                for move in available_moves:
                    if cell == move:
                        return piece, move
        return None, None

    def _find_winner_move(self, board, positions, piece_type, board_size):
        """
        Finds a winning move for the given piece type by checking available moves.

        Args:
            board (list): The current state of the game board.
            positions (list): The positions of the pieces to check for winning moves.
            piece_type (PieceType): The type of the pieces (e.g., white or black).
            board_size (int): The size of the board.

        Returns:
            tuple: The piece and its winning move if a winning move is found, or (None, None) if not.
        """
        for piece in positions:
            available_moves = get_available_cells_to_move(board, piece[0], piece[1], board_size)
            for move in available_moves:
                is_wins, winning_list = check_if_move_wins(board, move[0], move[1], piece_type, board_size)
                if is_wins and piece not in winning_list:
                    return piece, move
        return None, None

            