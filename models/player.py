from PyQt5.QtCore import pyqtSignal
from utils import PieceType, WIN_CONDITION
import copy
import random

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


def get_available_cells_in_direction(board, piece, row_step, col_step, max_size):
    """
    Returns a list of available cells in the specified direction until a non-empty cell is encountered.

    Args:
        board (list): The game board.
        piece (tuple): The starting position of the piece as a tuple (row, column).
        row_step (int): The row step to move in the specified direction.
        col_step (int): The column step to move in the specified direction.
        max_size (int): The maximum size of the board.

    Returns:
        list: A list of available cells in the specified direction as tuples (row, column).
    """
    available_cells = []
    row, col = piece[0], piece[1]
    i, j = row + row_step, col + col_step
    print("stuck here ", i, j, row_step, col_step)
    while 0 <= i < max_size and 0 <= j < max_size:
        if board[i][j] is PieceType.EMPTY:
            available_cells.append((i, j))
            i += row_step
            j += col_step
        else:
            break
    return available_cells

def check_consecutive_pieces_in_direction(board, move, piece_type, max_size, row_step, col_step):
    """
    Checks for consecutive pieces of a given type in a specific direction on the board, 
    starting from the given position and moving according to the provided row and column steps.

    Args:
        board (list): A 2D list representing the game board.
        move (tuple): The starting position on the board as a tuple (row, column).
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

    row, col = move[0], move[1]
    i, j = row + row_step, col + col_step
    while 0 <= i < max_size and 0 <= j < max_size:
        if board[i][j] == piece_type:
            consecutive_pieces.append((i, j))  
            i += row_step
            j += col_step
        else:
            break
    return len(consecutive_pieces), consecutive_pieces

def check_consecutive_pieces(board, move, piece_type, max_size, consecutive_needed):
    """
    Checks if the current move results in a consecutive sequence of the same piece type
    in any direction (horizontal, vertical, diagonal, and anti-diagonal).

    Args:
        board (list): The game board as a 2D list.
        move (tuple): The position of the current move as a tuple (row, column).
        piece_type (PieceType): The type of the piece being moved.
        max_size (int): The size of the board (number of rows/columns).
        consecutive_needed (int): The number of consecutive pieces needed to win.

    Returns:
        tuple: (bool, list) 
               - True and the list of winning positions if the move results in a win.
               - False and an empty list otherwise.
    """
    # Helper function to combine results
    def check_and_collect(direction_func):
        count, positions = direction_func(board, move, piece_type, max_size)
        return count, positions

    # Check horizontal
    consecutive_row_right, right_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, 0, 1))
    consecutive_row_left, left_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, 0, -1))
    total_consecutive_row = consecutive_row_right + consecutive_row_left + 1  # Include the current piece
    if total_consecutive_row >= consecutive_needed:
        row_positions = right_positions + [move] + left_positions
        return True, row_positions

    # Check vertical
    consecutive_col_down, down_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, 1, 0))
    consecutive_col_up, up_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, -1, 0))
    total_consecutive_col = consecutive_col_down + consecutive_col_up + 1  # Include the current piece
    if total_consecutive_col >= consecutive_needed:
        col_positions = down_positions + [move] + up_positions
        return True, col_positions

    # Check diagonal (top-left to bottom-right)
    consecutive_diag_top_right, top_right_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, -1, 1))
    consecutive_diag_bottom_left, bottom_left_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, 1, -1))
    total_consecutive_diag = consecutive_diag_top_right + consecutive_diag_bottom_left + 1  # Include the current piece
    if total_consecutive_diag >= consecutive_needed:
        diag_positions = top_right_positions + [move] + bottom_left_positions
        return True, diag_positions

    # Check anti-diagonal (top-right to bottom-left)
    consecutive_anti_diag_top_left, top_left_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, -1, -1))
    consecutive_anti_diag_bottom_right, bottom_right_positions = check_and_collect(lambda *args: check_consecutive_pieces_in_direction(*args, 1, 1))
    total_consecutive_anti_diag = consecutive_anti_diag_top_left + consecutive_anti_diag_bottom_right + 1  # Include the current piece
    if total_consecutive_anti_diag >= consecutive_needed:
        anti_diag_positions = top_left_positions + [move] + bottom_right_positions
        return True, anti_diag_positions

    return False, []


def get_available_cells_to_move(board, piece, max_size):
    """
    Gets all available cells that a piece can move to from a specific position.

    Args:
        board (list): The game board as a 2D list.
        piece (tuple): The current position of the piece as a tuple (row, column).
        max_size (int): The size of the board (number of rows/columns).

    Returns:
        list: A list of available cells where the piece can move, represented as tuples (row, column).
    """
    available_cells = []

    # Horizontal directions
    available_cells.extend(get_available_cells_in_direction(board, piece, 0, 1, max_size))  # Right
    available_cells.extend(get_available_cells_in_direction(board, piece, 0, -1, max_size))  # Left

    # Vertical directions
    available_cells.extend(get_available_cells_in_direction(board, piece, 1, 0, max_size))  # Down
    available_cells.extend(get_available_cells_in_direction(board, piece, -1, 0, max_size))  # Up

    # Diagonal directions
    available_cells.extend(get_available_cells_in_direction(board, piece, -1, 1, max_size))  # Top-right
    available_cells.extend(get_available_cells_in_direction(board, piece, 1, -1, max_size))  # Bottom-left

    # Anti-diagonal directions
    available_cells.extend(get_available_cells_in_direction(board, piece, -1, -1, max_size))  # Top-left
    available_cells.extend(get_available_cells_in_direction(board, piece, 1, 1, max_size))  # Bottom-right

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
        self._first_turn_played = False

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
        self._positions.append(point)

    def update_positions(self):
        """
        Updates the player's positions after a move.
        """
        self._positions.remove(self._move['from'])
        self._positions.append(self._move['to'])

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

    def reset_data(self):
        self._move_num = 0
        self._positions.clear()
        self._first_turn_played = False

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

    def _change_piece_pos(self, board, from_pos, to_pos, piece_type):
        board[from_pos[0]][from_pos[1]] = PieceType.EMPTY
        board[to_pos[0]][to_pos[1]] = piece_type

    def _attempt_winning_move(self, board, positions, piece_type, board_size):
        winning_moves = self._find_consecutive_moves(board, positions, piece_type, board_size, WIN_CONDITION)
        if winning_moves:
            from_move, to_move, _ = random.choice(winning_moves)
            return (from_move, to_move)
        return None

    def _block_winning_move(self, board, positions, other_player_positions, other_player_type, board_size):
        winning_moves = self._find_consecutive_moves(board, other_player_positions, other_player_type, board_size, WIN_CONDITION)
        if winning_moves:
            random.shuffle(winning_moves)
            for winning_move in winning_moves:
                from_move, to_move = self._try_to_block_move(board, positions, winning_move[0], winning_move[1], board_size)
                if from_move:
                    return (from_move, to_move)
        return None

    def _make_random_move(self, board, positions, other_player_positions, board_size):
        other_player_type = PieceType.WHITE if self._piece_type == PieceType.BLACK else PieceType.BLACK
        move = None
        while not move:
            piece_pos = random.choice(positions)
            available_moves = get_available_cells_to_move(board, piece_pos, board_size)
            if available_moves:
                to_move = random.choice(available_moves)
                self._change_piece_pos(board, piece_pos, to_move, self._piece_type)
                is_opponent_will_win = self._check_if_opponent_can_win(board, piece_pos, to_move, other_player_positions, other_player_type, board_size)
                self._change_piece_pos(board, to_move, piece_pos, self._piece_type)
                if not is_opponent_will_win or len(positions) == 1: # return move if the other player is not winning or if I removed all the pieces and he will win anyway
                    move = (piece_pos, to_move)
                else:
                    positions.remove(piece_pos)
                
        return move

    def _check_if_opponent_can_win(self, board, piece_pos, to_move, other_player_positions, other_player_type, board_size):
        """
        Checks if the opponent can win after making a move.

        Args:
            board (list): The current state of the game board.
            piece_pos (tuple): The current position of the player's piece.
            to_move (tuple): The position to move the player's piece to.
            other_player_positions (list): Positions of the opponent's pieces.
            other_player_type (PieceType): The type of the opponent's pieces.
            board_size (int): The size of the board.

        Returns:
            bool: True if the opponent can win after the move, False otherwise.
        """
        for other_piece_pos in other_player_positions:
            other_available_moves = get_available_cells_to_move(board, other_piece_pos, board_size)
            for move in other_available_moves:
                self._change_piece_pos(board, other_piece_pos, move, other_player_type)
                is_opponent_will_win, _ = check_consecutive_pieces(board, move, other_player_type, board_size, WIN_CONDITION)
                self._change_piece_pos(board, move, other_piece_pos, other_player_type)
                if is_opponent_will_win:
                    return  True

        return False

    def _set_move(self, from_move, to_move):
        """
        Sets the move's from and to positions.

        Args:
            from_move (tuple): The initial position of the piece.
            to_move (tuple): The target position of the piece.
        """
        self.set_from_move(from_move[0], from_move[1])
        self.set_to_move(to_move[0], to_move[1])


    def _try_to_block_move(self, board, positions, from_move, to_move, board_size):
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
            for piece in positions:
                available_moves = get_available_cells_to_move(board, piece, board_size)
                for move in available_moves:
                    if cell == move:
                        return piece, move
        return None, None

    def _find_consecutive_moves(self, board, positions, piece_type, board_size, consecutive_needed):
        """
        Finds possible moves that form consecutive pieces based on the given condition.

        Args:
            consecutive_needed (int): The number of consecutive pieces required.

        Returns:
            list: A list of tuples, each containing (original_position, new_position, consec_list).
        """
        moves_for_consecutive = []
        for position in positions:
            available_moves = get_available_cells_to_move(board, position, board_size)
            if available_moves:
                for to_move in available_moves:
                    self._change_piece_pos(board, position, to_move, piece_type)
                    is_consecutive, consec_list = check_consecutive_pieces(board, to_move, piece_type, board_size, consecutive_needed)
                    self._change_piece_pos(board, to_move, position, piece_type)
                    if is_consecutive:
                        moves_for_consecutive.append((position, to_move, consec_list))   
        return moves_for_consecutive

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
        new_move = None
        board_copy = copy.deepcopy(board)
        positions_copy = copy.deepcopy(self._positions)

        # Check if the player can win in a single move
        new_move = self._attempt_winning_move(board_copy, positions_copy, self._piece_type, board_size)

        # Check if the opponent can win and block if necessary
        if not new_move:
            other_player_type = PieceType.WHITE if self._piece_type == PieceType.BLACK else PieceType.BLACK
            new_move = self._block_winning_move(board_copy, positions_copy, other_player_positions, other_player_type, board_size)

        # If no critical moves found, make a random move
        if not new_move:
            new_move = self._make_random_move(board_copy, positions_copy, other_player_positions, board_size)

        self._set_move(*new_move)
        self.set_move_waiting_time(0.1)
        return copy.deepcopy(self._move)

class AiPlayerMedium(Player):
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

    def _get_consecutive_extensions(self, points, size):
        """
        Calculate the possible consecutive points that extend a line formed by the input points.

        This function takes a list of consecutive points and calculates potential extensions of
        the line in both forward and backward directions, based on the consistent direction of the 
        input points. The function ensures that all points are aligned in the same direction and
        checks if the extended points lie within the bounds of the board.

        Args:
            points (list of tuples): A list of tuples where each tuple represents a point as (row, col).
                                    The points must be consecutive and aligned in the same direction.
            size (int): The size of the board (assumed to be square) which sets the boundary for valid points.

        Returns:
            list of tuples: A list containing up to two points that extend the line in both directions.
                            Each point is represented as a tuple (row, col). The points will only be returned
                            if they lie within the boundaries of the board. If no valid extension is possible,
                            an empty list is returned.
        """
        if len(points) < 2:
            return []

        # Calculate the direction vector
        dx = points[1][0] - points[0][0]
        dy = points[1][1] - points[0][1]

        # Ensure all points are in the same direction
        for i in range(1, len(points)):
            curr_dx = points[i][0] - points[i - 1][0]
            curr_dy = points[i][1] - points[i - 1][1]
            if (curr_dx, curr_dy) != (dx, dy):
                return []

        # Calculate the next points in both directions
        next_point_forward = (points[-1][0] + dx, points[-1][1] + dy)
        next_point_backward = (points[0][0] - dx, points[0][1] - dy)

        # Check if the points are within the board boundaries
        valid_points = []
        for x, y in [next_point_backward, next_point_forward]:
            if 0 <= x < size and 0 <= y < size:
                valid_points.append((x, y))
        return valid_points

    def _available_extentions(self, board, positions, board_size, winning_points):
        point_a, point_b = winning_points
        found_a, found_b = False, False
        for position in positions:
            available_moves = get_available_cells_to_move(board, position, board_size)
            for move in available_moves:
                if move == point_a:
                    found_a = True
                if move == point_b:
                    found_b = True
                if found_a and found_b:
                    return 2
        if found_a or found_b:
            return 1
        return 0

    @staticmethod
    def _get_the_best_optional_move(optional_moves):
        list_1 = []
        list_2 = []

        # Iterate through the list once and split into two lists
        for optional_move in optional_moves:
            if optional_move[2] == 1:
                list_1.append(optional_move)
            elif optional_move[2] == 2:
                list_2.append(optional_move)
        
        if len(list_2) != 0:
            chosen_move = random.choice(list_2)
        else:
            chosen_move = random.choice(list_1)

        return chosen_move

    def _attack_opponent(self, board_copy, positions_copy, other_player_positions_cp, other_player_type, board_size):
        """
        Attempts to find the best optional move based on forming three consecutive pieces.

        Args:
            board_copy (list): A copy of the game board.
            positions_copy (list): A copy of the player's piece positions.
            other_player_positions_cp (list): A copy of the opponent's piece positions.
            other_player_type (PieceType): The type of the opponent's pieces.
            board_size (int): The size of the board.

        Returns:
            tuple: The best move (from_move, to_move) and winning options value, or (None, None) if no move found.
        """
        optional_moves = []
        moves_for_3 = self._find_consecutive_moves(board_copy, positions_copy, self._piece_type, board_size, 3)
        for from_move, to_move, consec_pieces in moves_for_3:
            points_that_win = self._get_consecutive_extensions(consec_pieces, board_size)
            self._change_piece_pos(board_copy, from_move, to_move, self._piece_type)
            if len(points_that_win) == 2:
                options_to_win = self._available_extentions(board_copy, positions_copy, board_size, points_that_win)
                if options_to_win == 2:
                    optional_moves.append((from_move, to_move, 2))
                elif options_to_win == 1:
                    blocking_move = self._block_winning_move(board_copy, positions_copy, other_player_positions_cp, other_player_type, board_size)
                    if not blocking_move:
                        optional_moves.append((from_move, to_move, 2))
                    else:
                        optional_moves.append((from_move, to_move, 1))
            elif len(points_that_win) == 1:
                winning_move = self._attempt_winning_move(board_copy, positions_copy, self._piece_type, board_size)
                if winning_move:
                    optional_moves.append((from_move, to_move, 1))
            self._change_piece_pos(board_copy, to_move, from_move, self._piece_type)

        new_move = None
        winning_options = None
        while not new_move and len(optional_moves) != 0:
            from_move, to_move, winning_options = self._get_the_best_optional_move(optional_moves)
            self._change_piece_pos(board_copy, from_move, to_move, self._piece_type)
            is_opponent_will_win = self._check_if_opponent_can_win(board_copy, positions_copy, to_move, other_player_positions_cp, other_player_type, board_size)
            self._change_piece_pos(board_copy, to_move, from_move, self._piece_type)
            if not is_opponent_will_win:
                new_move = (from_move, to_move)
            else:
                optional_moves.remove((from_move, to_move, winning_options))

        return new_move, winning_options

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
        new_move = None
        board_copy = copy.deepcopy(board)
        positions_copy = copy.deepcopy(self._positions)

        print("pos ", self._positions)
        print("other pos ", other_player_positions)
        # Check if the player can win in a single move
        new_move = self._attempt_winning_move(board_copy, positions_copy, self._piece_type, board_size)

        # Check if the opponent can win and block if necessary
        if not new_move:
            other_player_type = PieceType.WHITE if self._piece_type == PieceType.BLACK else PieceType.BLACK
            new_move = self._block_winning_move(board_copy, positions_copy, other_player_positions, other_player_type, board_size)
        
        # Try to find the best optional move
        if not new_move and self._first_turn_played:
            new_move, winning_options = self._attack_opponent(board_copy, positions_copy, other_player_positions, other_player_type, board_size)

        # If no critical moves found, make a random move
        if not new_move:
            new_move = self._make_random_move(board_copy, positions_copy, other_player_positions, board_size)

        self._set_move(*new_move)
        self.set_move_waiting_time(0.1)
        self._first_turn_played = True
        return copy.deepcopy(self._move)
