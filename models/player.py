from PyQt5.QtCore import pyqtSignal
from typing import List, Tuple, Optional
from utils import PieceType, WIN_CONDITION
import copy
import random
import time
import bisect 

AI_MOVE_WAITING_TIME = 1.5

def get_pieces_that_can_move_to_target(
    board: List[List],
    pieces_positions: List[Tuple[int, int]],
    target_cell: Tuple[int, int],
    board_size: int
) -> List[Tuple[int, int]]:
    """
    Identifies which pieces can move to the specified target cell.

    Parameters:
        - board (list of lists): The current game board.
        - pieces_positions (list of tuples): The current positions of the player's pieces.
        - target_cell (tuple): The target cell to move a piece to.
        - board_size (int): The size of the game board.

    Returns:
        - list of tuples: Positions of the pieces that can move to the target cell.
    """
    movable_pieces = []
    for piece_pos in pieces_positions:
        available_moves = get_available_cells_to_move(board, piece_pos, board_size)
        if available_moves and target_cell in available_moves:
            movable_pieces.append(piece_pos)
    return movable_pieces

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
        """
        Resets the internal game data to its initial state.

        This method performs the following actions:
        - Resets the move counter (`_move_num`) to 0.
        - Clears the list or dictionary of positions (`_positions`), removing any previous game data.
        - Sets the `_first_turn_played` flag to False, indicating that the first turn has not yet been played.
        
        This function is typically called when starting a new game or resetting the current game state.
        """
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
        """
        Moves a piece from one position to another on the board.

        Parameters:
        - board (list of lists): The current game board, represented as a 2D array.
        - from_pos (tuple): The current position of the piece (row, column).
        - to_pos (tuple): The target position for the piece (row, column).
        - piece_type (PieceType): The type of piece being moved.

        This function sets the `from_pos` cell to empty and updates the `to_pos` cell with the provided piece type.
        """
        board[from_pos[0]][from_pos[1]] = PieceType.EMPTY
        board[to_pos[0]][to_pos[1]] = piece_type


    def _attempt_winning_move(self, board, positions, piece_type, board_size):
        """
        Attempts to make a winning move by checking for possible sequences that meet the winning condition.

        Parameters:
        - board (list of lists): The current game board, represented as a 2D array.
        - positions (list of tuples): The current positions of all pieces of the given type.
        - piece_type (PieceType): The type of piece to check for a winning move.
        - board_size (int): The size of the game board (e.g., width and height).

        Returns:
        - tuple: A move as a tuple of (from_position, to_position) if a winning move is found.
        - None: If no winning move is found.

        This function finds all possible winning moves and randomly selects one.
        """
        winning_moves = self._find_consecutive_moves(board, positions, piece_type, board_size, WIN_CONDITION)
        if winning_moves:
            from_move, to_move, _ = random.choice(winning_moves)
            return (from_move, to_move)
        return None


    def _block_winning_move(self, board, positions, other_player_positions, other_player_type, board_size):
        """
        Attempts to block the opponent's winning move by finding sequences that could lead to a win for the opponent.

        Parameters:
        - board (list of lists): The current game board, represented as a 2D array.
        - positions (list of tuples): The current positions of all pieces of the current player.
        - other_player_positions (list of tuples): The current positions of the opponent's pieces.
        - other_player_type (PieceType): The type of piece used by the opponent.
        - board_size (int): The size of the game board (e.g., width and height).

        Returns:
        - tuple: A move as a tuple of (from_position, to_position) if a blocking move is found.
        - None: If no blocking move is found.

        This function tries to block the opponent's winning move by shuffling the list of potential winning moves and evaluating them.
        """
        ret = None
        winning_moves = self._find_consecutive_moves(board, other_player_positions, other_player_type, board_size, WIN_CONDITION)
        if winning_moves:
            random.shuffle(winning_moves)
            for winning_move in winning_moves:
                blocking_moves = self._try_to_block_move(board, positions, winning_move[0], winning_move[1], board_size)
                for from_move, to_move in blocking_moves:
                    ret = (from_move, to_move)
                    if self._evaluate_move(board, from_move, to_move, other_player_positions, other_player_type, board_size):
                        break
        return ret


    def _evaluate_move(
        self,
        board: List[List],
        piece_pos: Tuple[int, int],
        to_move: Tuple[int, int],
        other_player_positions: List[Tuple[int, int]],
        other_player_type,
        board_size: int
    ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Evaluates a move to determine if it's safe or if the opponent can win.

        Parameters:
            - board (list of lists): The current game board.
            - piece_pos (tuple): The current position of the player's piece.
            - to_move (tuple): The position to move the piece to.
            - other_player_positions (list of tuples): Opponent's piece positions.
            - other_player_type: The type of the opponent's pieces.
            - board_size (int): The size of the game board.

        Returns:
            - tuple: The move as (from_position, to_position) if it's safe or should be taken.
            - None: If the move is not safe and should be skipped.
        """
        # Simulate the move
        self._change_piece_pos(board, piece_pos, to_move, self._piece_type)
        
        # Check if the opponent can win after this move
        is_opponent_will_win, winning_move = self._check_if_opponent_can_win(
            board, piece_pos, to_move, other_player_positions, other_player_type, board_size
        )
        
        # Undo the move
        self._change_piece_pos(board, to_move, piece_pos, self._piece_type)
        
        if is_opponent_will_win:
            opponent_route = get_all_cells_in_route(winning_move[0], winning_move[1])

            # If our piece is in the opponent's winning route, skip this move
            if piece_pos in opponent_route:
                return None  # Unsafe move, skip
            else:
                # Opponent will win, but our piece is not in the route
                return (piece_pos, to_move)
        else:
            # Opponent will not win; this is a safe move
            return (piece_pos, to_move)

    def _make_random_move(
        self,
        board: List[List],
        positions: List[Tuple[int, int]],
        other_player_positions: List[Tuple[int, int]],
        board_size: int
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Makes a random move while trying to prevent the opponent from winning.

        Parameters:
            - board (list of lists): The current game board, represented as a 2D array.
            - positions (list of tuples): The current positions of the player's pieces.
            - other_player_positions (list of tuples): The current positions of the opponent's pieces.
            - board_size (int): The size of the game board (e.g., width and height).

        Returns:
            - tuple: A random move as a tuple of (from_position, to_position).

        This function iterates over all available moves for the player's pieces, checks if the opponent will win based on the move, and makes a safe random move. If no safe move is found, it selects any random move.
        """
        other_player_type = PieceType.WHITE if self._piece_type == PieceType.BLACK else PieceType.BLACK
        available_positions_moves = []

        # Gather all available moves for each piece
        for piece_pos in positions:
            available_moves = get_available_cells_to_move(board, piece_pos, board_size)
            if available_moves:
                available_positions_moves.append((piece_pos, available_moves))

        # Shuffle to ensure randomness
        random.shuffle(available_positions_moves)

        # Iterate through each piece and its available moves
        for piece_pos, available_moves in available_positions_moves:
            random.shuffle(available_moves)  # Randomize the move order
            for to_move in available_moves:
                move_result = self._evaluate_move(board, piece_pos, to_move, other_player_positions, other_player_type, board_size)
                if move_result:
                    return move_result  # Return the first safe move found

        # If no safe move is found, choose any available move
        if available_positions_moves:
            piece_pos, available_moves = available_positions_moves[0]
            to_move = available_moves[0]
            return (piece_pos, to_move)
        else:
            raise ValueError("No available moves to make.")


    def _check_if_opponent_can_win(self, board, piece_pos, to_move, other_player_positions, other_player_type, board_size):
        """
        Checks if the opponent can win after the current player makes a move.

        This function temporarily moves each of the opponent's pieces to check if any move would result in a win
        for the opponent. It simulates the opponent's possible moves and reverses the board state after each check.

        Parameters:
        - board (list of lists): The current game board, represented as a 2D array.
        - piece_pos (tuple): The current position of the player's piece (row, column).
        - to_move (tuple): The position to move the player's piece to (row, column).
        - other_player_positions (list of tuples): The current positions of the opponent's pieces.
        - other_player_type (PieceType): The type of piece used by the opponent.
        - board_size (int): The size of the game board (e.g., width and height).

        Returns:
        - bool: True if the opponent can win after the current player's move, False otherwise.
        - tuple or None: The opponent's winning move as a tuple of (from_position, to_position) if a winning move is found.
        Returns None if no winning move is found.

        This function simulates potential moves for the opponent and checks if any of them would satisfy the win condition.
        """
        for other_piece_pos in other_player_positions:
            other_available_moves = get_available_cells_to_move(board, other_piece_pos, board_size)
            for move in other_available_moves:
                self._change_piece_pos(board, other_piece_pos, move, other_player_type)
                is_opponent_will_win, _ = check_consecutive_pieces(board, move, other_player_type, board_size, WIN_CONDITION)
                self._change_piece_pos(board, move, other_piece_pos, other_player_type)
                if is_opponent_will_win:
                    return True, (other_piece_pos, move)
        return False, None


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
            list: The avaiable blocking pieces and its new positions, or empty list if no block is found.
        """
        cells = get_all_cells_in_route(from_move, to_move)
        blocking_moves = []
        for cell in cells:
            for piece in positions:
                available_moves = get_available_cells_to_move(board, piece, board_size)
                for move in available_moves:
                    if cell == move:
                        blocking_moves.append((piece, move))
        return blocking_moves

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
            for to_move in available_moves:
                self._change_piece_pos(board, position, to_move, piece_type)
                is_consecutive, consec_list = check_consecutive_pieces(board, to_move, piece_type, board_size, consecutive_needed)
                self._change_piece_pos(board, to_move, position, piece_type)
                if is_consecutive:
                    moves_for_consecutive.append((position, to_move, consec_list))   
        return moves_for_consecutive

    def _apply_move(self, board, positions, from_move, to_move, piece_type):
        self._change_piece_pos(board, from_move, to_move, piece_type)
        positions.remove(from_move)
        positions.append(to_move)

    def _undo_move(self, board, positions, from_move, to_move, piece_type):
        self._change_piece_pos(board, to_move, from_move, piece_type)
        positions.remove(to_move)
        positions.append(from_move)

    def _board_key(self, board, piece_type_to_move):
        flat = tuple(cell.value for row in board for cell in row)
        return (piece_type_to_move.value, flat)

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
        self.set_move_waiting_time(AI_MOVE_WAITING_TIME)
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

        # Calculate the direction vector based on the first two points
        dx = points[1][0] - points[0][0]
        dy = points[1][1] - points[0][1]

        if dx == 0 and dy == 0:
            # All points are the same
            return []

        # Sort the points based on their position along the direction vector
        # Calculate a projection value for each point
        x0, y0 = points[0]
        def projection(point):
            x, y = point
            return (x - x0) * dx + (y - y0) * dy

        sorted_points = sorted(points, key=projection)

        # Recalculate the direction vector based on the sorted points
        dx = sorted_points[1][0] - sorted_points[0][0]
        dy = sorted_points[1][1] - sorted_points[0][1]

        if dx == 0 and dy == 0:
            # All points are the same after sorting
            return []

        # Ensure all points are in the same direction
        for i in range(1, len(sorted_points)):
            curr_dx = sorted_points[i][0] - sorted_points[i - 1][0]
            curr_dy = sorted_points[i][1] - sorted_points[i - 1][1]
            if (curr_dx, curr_dy) != (dx, dy):
                return []

        # Calculate the next points in both directions
        next_point_forward = (sorted_points[-1][0] + dx, sorted_points[-1][1] + dy)
        next_point_backward = (sorted_points[0][0] - dx, sorted_points[0][1] - dy)

        # Check if the points are within the board boundaries
        valid_points = []
        for x, y in [next_point_backward, next_point_forward]:
            if 0 <= x < size and 0 <= y < size:
                valid_points.append((x, y))
        return valid_points


    def _available_extentions(self, board, positions, board_size, winning_points, points_to_skip):
        point_a, point_b = winning_points
        found_a, found_b = False, False
        for position in positions:
            if position in points_to_skip:
                continue
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
        """
        Selects the best optional move based on priority.

        Parameters:
        - optional_moves (list of tuples): A list of potential moves, where each move is a tuple that contains:
            - The move's 'from' position.
            - The move's 'to' position.
            - A priority indicator (1 or 2), where 2 indicates a higher priority move.

        Returns:
        - tuple: A randomly chosen move from the highest-priority group (priority 2 if available, otherwise priority 1).

        This function separates the optional moves into two lists based on their priority.
        If there are any priority 2 moves, one is chosen randomly. If there are no priority 2 moves, a priority 1 move is randomly chosen instead.
        """
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

    def _block_a_force_win(self, board, positions, other_player_positions, other_player_type, board_size):
        move = None
        winning_move, winning_options = self._find_attack(board, other_player_positions, positions, other_player_type, self._piece_type, board_size)
        if winning_move and winning_options == 2:
            blocking_options = get_pieces_that_can_move_to_target(board, positions, winning_move[1], board_size)
            for piece_pos in blocking_options:
                new_move = self._evaluate_move(board, piece_pos, winning_move[1], other_player_positions, other_player_type, board_size)
                if new_move:
                    move = new_move
                    break
        return move

    def _find_attack(self, board, positions, other_player_positions, piece_type, other_piece_type, board_size):
        optional_moves = []
        positions_cp = copy.deepcopy(positions)
        other_player_positions_cp = copy.deepcopy(other_player_positions)
        moves_for_3 = self._find_consecutive_moves(board, positions, piece_type, board_size, 3)
        for from_move, to_move, consec_pieces in moves_for_3:
            points_that_win = self._get_consecutive_extensions(consec_pieces, board_size)
            self._apply_move(board, positions_cp, from_move, to_move, piece_type)
            if len(points_that_win) == 2:
                options_to_win = self._available_extentions(board, positions_cp, board_size, points_that_win, consec_pieces)
                if options_to_win == 2:
                    optional_moves.append((from_move, to_move, 2))
                elif options_to_win == 1:
                    blocking_move = self._block_winning_move(board, other_player_positions, positions_cp, piece_type, board_size)
                    if blocking_move:
                        optional_moves.append((from_move, to_move, 1))
                    else:
                        optional_moves.append((from_move, to_move, 2))
            elif len(points_that_win) == 1:
                winning_move = self._attempt_winning_move(board, positions_cp, piece_type, board_size)
                if winning_move:
                    blocking_move = self._block_winning_move(board, other_player_positions, positions_cp, piece_type, board_size)
                    if blocking_move:
                        optional_moves.append((from_move, to_move, 1))
                    else:
                        optional_moves.append((from_move, to_move, 2))
            self._undo_move(board, positions_cp, from_move, to_move, piece_type)

        new_move = None
        winning_options = None
        while not new_move and len(optional_moves) != 0:
            from_move, to_move, winning_options = self._get_the_best_optional_move(optional_moves)
            self._change_piece_pos(board, from_move, to_move, piece_type)
            is_opponent_will_win, _ = self._check_if_opponent_can_win(board, positions, to_move, other_player_positions, other_piece_type, board_size)
            self._change_piece_pos(board, to_move, from_move, piece_type)
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

        # Check if the player can win in a single move
        new_move = self._attempt_winning_move(board_copy, positions_copy, self._piece_type, board_size)

        # Check if the opponent can win and block it
        if not new_move:
            other_player_type = PieceType.WHITE if self._piece_type == PieceType.BLACK else PieceType.BLACK
            new_move = self._block_winning_move(board_copy, positions_copy, other_player_positions, other_player_type, board_size)
        
        # check if the opponent can force a win and block it
        if not new_move:
            new_move = self._block_a_force_win(board_copy, positions_copy, other_player_positions, other_player_type, board_size)

        # Try to find the best optional move
        if not new_move and self._first_turn_played:
            new_move, winning_options = self._find_attack(board_copy, positions_copy, other_player_positions, self._piece_type, other_player_type, board_size)

        # If no critical moves found, make a random move
        if not new_move:
            new_move = self._make_random_move(board_copy, positions_copy, other_player_positions, board_size)

        self._set_move(*new_move)
        self.set_move_waiting_time(AI_MOVE_WAITING_TIME)
        self._first_turn_played = True
        return copy.deepcopy(self._move)


class AiPlayerHard(Player):
    """
    Hard AI using bitboards internally.

    Features:
    - bitboard representation
    - fast legal move generation with precomputed rays
    - immediate win detection
    - safe block detection
    - double-threat creation detection
    - alpha-beta negamax
    - tactical extension in sharp positions
    - profiling summary per move
    """

    WIN_SCORE = 10_000_000
    DRAW_SCORE = 0

    CENTER_WEIGHT = 6
    IMMEDIATE_WIN_BONUS = 120_000
    DOUBLE_THREAT_BONUS = 80_000
    FORCED_THREAT_BONUS = 25_000
    REACHABLE_EMPTY_BONUS = 12
    UNREACHABLE_EMPTY_PENALTY = 8

    LINE_SCORES = {
        0: 0,
        1: 8,
        2: 40,
        3: 400,
    }

    PROFILE_ENABLED = True
    PROFILE_PRINT_EVERY_MOVE = True

    TACTICAL_EXTENSION_LIMIT = 1

    def __init__(self, name, player_type, difficulty, piece_type, piece_path, search_depth=4):
        super().__init__(name, player_type, difficulty, piece_type, piece_path)
        self._search_depth = search_depth

        self._line_cache = {}
        self._rays_cache = {}
        self._windows_by_sq_cache = {}
        self._rc_to_sq_cache = {}
        self._sq_to_rc_cache = {}

        self._eval_cache = {}
        self._move_cache = {}
        self._tactical_cache = {}

        self._prof = {}
        self._prof_counts = {}
        self._prof_counters = {}

    # ------------------------------------------------------------------
    # Profiling helpers
    # ------------------------------------------------------------------

    def _prof_reset(self):
        self._prof = {}
        self._prof_counts = {}
        self._prof_counters = {}

    def _prof_add(self, name, elapsed):
        if not self.PROFILE_ENABLED:
            return
        self._prof[name] = self._prof.get(name, 0.0) + elapsed
        self._prof_counts[name] = self._prof_counts.get(name, 0) + 1

    def _prof_inc(self, name, amount=1):
        if not self.PROFILE_ENABLED:
            return
        self._prof_counters[name] = self._prof_counters.get(name, 0) + amount

    def _prof_print_summary(self, total_elapsed, chosen_move):
        if not self.PROFILE_ENABLED or not self.PROFILE_PRINT_EVERY_MOVE:
            return

        print("\n" + "=" * 72)
        print(f"[AiPlayerHard] move summary | depth={self._search_depth} | move={chosen_move} | total={total_elapsed:.6f}s")
        print("-" * 72)

        rows = []
        for name, total in self._prof.items():
            calls = self._prof_counts.get(name, 0)
            avg = total / calls if calls else 0.0
            rows.append((total, name, calls, avg))

        rows.sort(reverse=True)

        print(f"{'function':35} {'calls':>10} {'total(s)':>12} {'avg(ms)':>12}")
        for total, name, calls, avg in rows:
            print(f"{name:35} {calls:10d} {total:12.6f} {avg * 1000:12.3f}")

        if self._prof_counters:
            print("-" * 72)
            print("counters:")
            for key in sorted(self._prof_counters.keys()):
                print(f"  {key}: {self._prof_counters[key]}")
        print("=" * 72)

    # ------------------------------------------------------------------
    # Main entry
    # ------------------------------------------------------------------

    def make_move(self, board, other_player_positions, board_size):
        total_start = time.perf_counter()
        self._prof_reset()

        self._move_cache = {}
        self._eval_cache = {}
        self._tactical_cache = {}

        self._ensure_precomputed(board_size)

        white_bits, black_bits, white_positions, black_positions = self._board_to_bitboards(board, board_size)

        if self._piece_type == PieceType.WHITE:
            my_bits = white_bits
            my_positions = white_positions
            opp_bits = black_bits
            opp_positions = black_positions
        else:
            my_bits = black_bits
            my_positions = black_positions
            opp_bits = white_bits
            opp_positions = white_positions

        # 1) immediate win
        t0 = time.perf_counter()
        winning_moves = self._get_winning_moves_bits(my_bits, my_positions, opp_bits, board_size)
        self._prof_add("_get_winning_moves_bits", time.perf_counter() - t0)
        if winning_moves:
            best_move_sq = self._order_candidate_moves_bits(
                winning_moves, my_bits, my_positions, opp_bits, opp_positions, board_size
            )[0]
            from_rc = self._sq_to_rc(best_move_sq[0], board_size)
            to_rc = self._sq_to_rc(best_move_sq[1], board_size)
            self._set_move(from_rc, to_rc)

            elapsed = time.perf_counter() - total_start
            self.set_move_waiting_time(max(0.0, AI_MOVE_WAITING_TIME - elapsed))
            self._first_turn_played = True
            self._prof_print_summary(elapsed, (from_rc, to_rc))
            return copy.deepcopy(self._move)

        # 2) immediate safe block
        t0 = time.perf_counter()
        safe_blockers = self._get_safe_blocking_moves_bits(
            my_bits, my_positions, opp_bits, opp_positions, board_size
        )
        self._prof_add("_get_safe_blocking_moves_bits", time.perf_counter() - t0)
        if safe_blockers:
            best_move_sq = self._order_candidate_moves_bits(
                safe_blockers, my_bits, my_positions, opp_bits, opp_positions, board_size
            )[0]
            from_rc = self._sq_to_rc(best_move_sq[0], board_size)
            to_rc = self._sq_to_rc(best_move_sq[1], board_size)
            self._set_move(from_rc, to_rc)

            elapsed = time.perf_counter() - total_start
            self.set_move_waiting_time(max(0.0, AI_MOVE_WAITING_TIME - elapsed))
            self._first_turn_played = True
            self._prof_print_summary(elapsed, (from_rc, to_rc))
            return copy.deepcopy(self._move)

        # 3) full search
        tt = {}
        t0 = time.perf_counter()
        _, best_move_sq = self._search_root_bits(
            current_bits=my_bits,
            current_positions=my_positions,
            other_bits=opp_bits,
            other_positions=opp_positions,
            board_size=board_size,
            depth=self._search_depth,
            extensions_left=self.TACTICAL_EXTENSION_LIMIT,
            tt=tt
        )
        self._prof_add("_search_root_bits", time.perf_counter() - t0)

        from_rc = self._sq_to_rc(best_move_sq[0], board_size)
        to_rc = self._sq_to_rc(best_move_sq[1], board_size)
        self._set_move(from_rc, to_rc)

        elapsed = time.perf_counter() - total_start
        self.set_move_waiting_time(max(0.0, AI_MOVE_WAITING_TIME - elapsed))
        self._first_turn_played = True

        self._prof_print_summary(elapsed, (from_rc, to_rc))
        return copy.deepcopy(self._move)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _search_root_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        other_positions,
        board_size,
        depth,
        extensions_left,
        tt
    ):
        alpha = -float("inf")
        beta = float("inf")

        best_score = -float("inf")
        best_moves = []

        t0 = time.perf_counter()
        moves = self._get_search_moves_bits(
            current_bits, current_positions, other_bits, other_positions, board_size
        )
        self._prof_add("_get_search_moves_bits", time.perf_counter() - t0)

        for from_sq, to_sq in moves:
            t0 = time.perf_counter()
            score = self._score_move_bits(
                current_bits=current_bits,
                current_positions=current_positions,
                other_bits=other_bits,
                other_positions=other_positions,
                from_sq=from_sq,
                to_sq=to_sq,
                board_size=board_size,
                depth=depth,
                extensions_left=extensions_left,
                alpha=alpha,
                beta=beta,
                ply=1,
                tt=tt,
                path_keys=set()
            )
            self._prof_add("_score_move_bits", time.perf_counter() - t0)

            if score > best_score:
                best_score = score
                best_moves = [(from_sq, to_sq)]
            elif score == best_score:
                best_moves.append((from_sq, to_sq))

            if score > alpha:
                alpha = score

        chosen_move = random.choice(best_moves) if best_moves else None
        return best_score, chosen_move

    def _score_move_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        other_positions,
        from_sq,
        to_sq,
        board_size,
        depth,
        extensions_left,
        alpha,
        beta,
        ply,
        tt,
        path_keys
    ):
        new_current_bits, new_current_positions = self._apply_move_bits(current_bits, current_positions, from_sq, to_sq)

        if self._is_win_after_move_bits(new_current_bits, to_sq, board_size):
            return self.WIN_SCORE - ply

        t0 = time.perf_counter()
        score = -self._negamax_bits(
            current_bits=other_bits,
            current_positions=other_positions,
            other_bits=new_current_bits,
            other_positions=new_current_positions,
            board_size=board_size,
            depth=depth - 1,
            extensions_left=extensions_left,
            alpha=-beta,
            beta=-alpha,
            ply=ply + 1,
            tt=tt,
            path_keys=path_keys
        )
        self._prof_add("_negamax_bits", time.perf_counter() - t0)

        return score

    def _negamax_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        other_positions,
        board_size,
        depth,
        extensions_left,
        alpha,
        beta,
        ply,
        tt,
        path_keys
    ):
        state_key = (current_bits, other_bits, depth, extensions_left)

        if state_key in path_keys:
            self._prof_inc("repetition_draws")
            return self.DRAW_SCORE

        tt_entry = tt.get(state_key)
        if tt_entry is not None:
            self._prof_inc("tt_hits")
            return tt_entry
        self._prof_inc("tt_misses")

        if depth == 0:
            if extensions_left > 0 and self._is_sharp_position_bits(
                current_bits, current_positions, other_bits, other_positions, board_size
            ):
                depth = 1
                extensions_left -= 1
            else:
                t0 = time.perf_counter()
                score = self._evaluate_position_bits(
                    current_bits, current_positions, other_bits, other_positions, board_size
                )
                self._prof_add("_evaluate_position_bits", time.perf_counter() - t0)
                tt[state_key] = score
                return score

        t0 = time.perf_counter()
        moves = self._get_search_moves_bits(
            current_bits, current_positions, other_bits, other_positions, board_size
        )
        self._prof_add("_get_search_moves_bits", time.perf_counter() - t0)

        best_score = -float("inf")
        path_keys.add(state_key)

        for from_sq, to_sq in moves:
            t0 = time.perf_counter()
            score = self._score_move_bits(
                current_bits=current_bits,
                current_positions=current_positions,
                other_bits=other_bits,
                other_positions=other_positions,
                from_sq=from_sq,
                to_sq=to_sq,
                board_size=board_size,
                depth=depth,
                extensions_left=extensions_left,
                alpha=alpha,
                beta=beta,
                ply=ply,
                tt=tt,
                path_keys=path_keys
            )
            self._prof_add("_score_move_bits", time.perf_counter() - t0)

            if score > best_score:
                best_score = score

            if best_score > alpha:
                alpha = best_score

            if alpha >= beta:
                self._prof_inc("alpha_beta_cutoffs")
                break

        path_keys.remove(state_key)
        tt[state_key] = best_score
        return best_score

    # ------------------------------------------------------------------
    # Search move selection
    # ------------------------------------------------------------------

    def _get_search_moves_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        other_positions,
        board_size
    ):
        winning_moves = self._get_winning_moves_bits(
            current_bits, current_positions, other_bits, board_size
        )
        if winning_moves:
            return self._order_candidate_moves_bits(
                winning_moves, current_bits, current_positions, other_bits, other_positions, board_size
            )

        safe_blockers = self._get_safe_blocking_moves_bits(
            current_bits, current_positions, other_bits, other_positions, board_size
        )
        if safe_blockers:
            return self._order_candidate_moves_bits(
                safe_blockers, current_bits, current_positions, other_bits, other_positions, board_size
            )

        double_threat_moves = self._get_double_threat_moves_bits(
            current_bits, current_positions, other_bits, board_size
        )
        if double_threat_moves:
            return self._order_candidate_moves_bits(
                double_threat_moves, current_bits, current_positions, other_bits, other_positions, board_size
            )

        return self._generate_ordered_moves_bits(
            current_bits, current_positions, other_bits, other_positions, board_size
        )

    def _generate_ordered_moves_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        other_positions,
        board_size
    ):
        all_legal = self._get_all_legal_moves_bits(
            current_bits, current_positions, other_bits, board_size
        )
        return self._order_candidate_moves_bits(
            all_legal, current_bits, current_positions, other_bits, other_positions, board_size
        )

    def _order_candidate_moves_bits(
        self,
        candidate_moves,
        current_bits,
        current_positions,
        other_bits,
        other_positions,
        board_size
    ):
        if not candidate_moves:
            return []

        occ_bits = current_bits | other_bits
        opp_targets_mask = self._get_immediate_win_targets_bits(
            other_bits, other_positions, current_bits, board_size
        )
        center = (board_size - 1) / 2.0

        scored = []

        for from_sq, to_sq in candidate_moves:
            score = 0

            new_current_bits, new_current_positions = self._apply_move_bits(
                current_bits, current_positions, from_sq, to_sq
            )

            if self._is_win_after_move_bits(new_current_bits, to_sq, board_size):
                score += 2_000_000

            opp_targets_after = self._get_immediate_win_targets_bits(
                other_bits, other_positions, new_current_bits, board_size
            )
            if opp_targets_after == 0:
                score += 300_000

            my_targets_after = self._get_immediate_win_targets_bits(
                new_current_bits, new_current_positions, other_bits, board_size
            )
            score += my_targets_after.bit_count() * 50_000

            if opp_targets_mask & (1 << to_sq):
                score += 20_000

            r, c = self._sq_to_rc(sq=to_sq, board_size=board_size)
            score -= int(abs(r - center) + abs(c - center)) * 3

            scored.append((score, from_sq, to_sq))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [(from_sq, to_sq) for score, from_sq, to_sq in scored]

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def _evaluate_position_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        other_positions,
        board_size
    ):
        key = ("eval_bits", current_bits, other_bits)
        cached = self._eval_cache.get(key)
        if cached is not None:
            self._prof_inc("eval_cache_hits")
            return cached
        self._prof_inc("eval_cache_misses")

        score = 0

        my_win_targets_mask = self._get_immediate_win_targets_bits(
            current_bits, current_positions, other_bits, board_size
        )
        opp_win_targets_mask = self._get_immediate_win_targets_bits(
            other_bits, other_positions, current_bits, board_size
        )

        my_distinct = my_win_targets_mask.bit_count()
        opp_distinct = opp_win_targets_mask.bit_count()

        if my_distinct >= 1:
            score += self.IMMEDIATE_WIN_BONUS
        if opp_distinct >= 1:
            score -= self.IMMEDIATE_WIN_BONUS

        if my_distinct >= 2:
            score += self.DOUBLE_THREAT_BONUS
        if opp_distinct >= 2:
            score -= self.DOUBLE_THREAT_BONUS

        my_double_threat_moves = self._get_double_threat_moves_bits(
            current_bits, current_positions, other_bits, board_size
        )
        opp_double_threat_moves = self._get_double_threat_moves_bits(
            other_bits, other_positions, current_bits, board_size
        )

        if my_double_threat_moves:
            score += self.DOUBLE_THREAT_BONUS // 2
        if opp_double_threat_moves:
            score -= self.DOUBLE_THREAT_BONUS // 2

        if self._opponent_has_forced_threat_next_turn_bits(
            current_bits, current_positions, other_bits, other_positions, board_size
        ):
            score -= self.FORCED_THREAT_BONUS

        if self._opponent_has_forced_threat_next_turn_bits(
            other_bits, other_positions, current_bits, current_positions, board_size
        ):
            score += self.FORCED_THREAT_BONUS

        line_windows = self._get_line_windows(board_size)

        my_reachable_mask = self._get_reachable_targets_mask_bits(
            current_bits, current_positions, other_bits, board_size
        )
        opp_reachable_mask = self._get_reachable_targets_mask_bits(
            other_bits, other_positions, current_bits, board_size
        )

        full_mask = (1 << (board_size * board_size)) - 1
        occ_bits = current_bits | other_bits
        empty_bits = full_mask ^ occ_bits

        for mask, _ in line_windows:
            my_count = (current_bits & mask).bit_count()
            opp_count = (other_bits & mask).bit_count()

            if my_count > 0 and opp_count > 0:
                continue

            empty_in_window = mask & empty_bits
            empty_count = empty_in_window.bit_count()

            if opp_count == 0:
                score += self.LINE_SCORES[my_count]
                reachable = (empty_in_window & my_reachable_mask).bit_count()
                score += reachable * self.REACHABLE_EMPTY_BONUS
                score -= (empty_count - reachable) * self.UNREACHABLE_EMPTY_PENALTY

            elif my_count == 0:
                score -= self.LINE_SCORES[opp_count]
                reachable = (empty_in_window & opp_reachable_mask).bit_count()
                score -= reachable * self.REACHABLE_EMPTY_BONUS
                score += (empty_count - reachable) * self.UNREACHABLE_EMPTY_PENALTY

        center = (board_size - 1) / 2.0
        my_center = 0
        opp_center = 0

        for sq in current_positions:
            r, c = self._sq_to_rc(sq, board_size)
            my_center -= abs(r - center) + abs(c - center)
        for sq in other_positions:
            r, c = self._sq_to_rc(sq, board_size)
            opp_center -= abs(r - center) + abs(c - center)

        score += int((my_center - opp_center) * self.CENTER_WEIGHT)

        self._eval_cache[key] = score
        return score

    # ------------------------------------------------------------------
    # Sharp state detection
    # ------------------------------------------------------------------

    def _is_sharp_position_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        other_positions,
        board_size
    ):
        key = ("sharp_bits", current_bits, other_bits)
        cached = self._tactical_cache.get(key)
        if cached is not None:
            return cached

        result = False

        if self._get_immediate_win_targets_bits(current_bits, current_positions, other_bits, board_size):
            result = True
        elif self._get_immediate_win_targets_bits(other_bits, other_positions, current_bits, board_size):
            result = True
        elif self._has_open_three_window_bits(current_bits, other_bits, board_size):
            result = True
        elif self._has_open_three_window_bits(other_bits, current_bits, board_size):
            result = True

        self._tactical_cache[key] = result
        return result

    # ------------------------------------------------------------------
    # Tactical helpers
    # ------------------------------------------------------------------

    def _get_winning_moves_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        board_size
    ):
        key = ("winning_moves_bits", current_bits, other_bits)
        cached = self._tactical_cache.get(key)
        if cached is not None:
            self._prof_inc("winning_moves_cache_hits")
            return cached

        self._prof_inc("winning_moves_cache_misses")

        targets_mask = self._get_immediate_win_targets_bits(
            current_bits, current_positions, other_bits, board_size
        )

        moves = []
        for target_sq in self._iter_bits(targets_mask):
            moves.extend(
                self._get_moves_to_target_bits(
                    current_bits, current_positions, other_bits, target_sq, board_size
                )
            )

        self._tactical_cache[key] = moves
        return moves

    def _get_safe_blocking_moves_bits(
        self,
        my_bits,
        my_positions,
        opp_bits,
        opp_positions,
        board_size
    ):
        key = ("safe_blockers_bits", my_bits, opp_bits)
        cached = self._tactical_cache.get(key)
        if cached is not None:
            self._prof_inc("safe_blockers_cache_hits")
            return cached

        self._prof_inc("safe_blockers_cache_misses")

        opp_targets_mask = self._get_immediate_win_targets_bits(
            opp_bits, opp_positions, my_bits, board_size
        )

        if opp_targets_mask == 0:
            self._tactical_cache[key] = []
            return []

        safe_moves = []
        all_legal = self._get_all_legal_moves_bits(my_bits, my_positions, opp_bits, board_size)

        for from_sq, to_sq in all_legal:
            new_my_bits, new_my_positions = self._apply_move_bits(
                my_bits, my_positions, from_sq, to_sq
            )

            opp_targets_after = self._get_immediate_win_targets_bits(
                opp_bits, opp_positions, new_my_bits, board_size
            )

            if opp_targets_after == 0:
                safe_moves.append((from_sq, to_sq))

        self._tactical_cache[key] = safe_moves
        return safe_moves

    def _get_double_threat_moves_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        board_size
    ):
        key = ("double_threat_moves_bits", current_bits, other_bits)
        cached = self._tactical_cache.get(key)
        if cached is not None:
            self._prof_inc("double_threat_moves_cache_hits")
            return cached

        self._prof_inc("double_threat_moves_cache_misses")

        all_legal = self._get_all_legal_moves_bits(
            current_bits, current_positions, other_bits, board_size
        )

        moves = []
        for from_sq, to_sq in all_legal:
            new_current_bits, new_current_positions = self._apply_move_bits(
                current_bits, current_positions, from_sq, to_sq
            )

            if self._is_win_after_move_bits(new_current_bits, to_sq, board_size):
                moves.append((from_sq, to_sq))
                continue

            targets_after = self._get_immediate_win_targets_bits(
                new_current_bits, new_current_positions, other_bits, board_size
            )

            if targets_after.bit_count() >= 2:
                moves.append((from_sq, to_sq))

        self._tactical_cache[key] = moves
        return moves

    def _opponent_has_forced_threat_next_turn_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        other_positions,
        board_size
    ):
        key = ("forced_bits", current_bits, other_bits)
        cached = self._tactical_cache.get(key)
        if cached is not None:
            self._prof_inc("forced_cache_hits")
            return cached

        self._prof_inc("forced_cache_misses")

        result = self._has_forcing_move_bits(
            other_bits, other_positions, current_bits, current_positions, board_size
        )

        self._tactical_cache[key] = result
        return result

    def _has_forcing_move_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        other_positions,
        board_size
    ):
        if self._get_winning_moves_bits(current_bits, current_positions, other_bits, board_size):
            return True

        return bool(
            self._get_double_threat_moves_bits(current_bits, current_positions, other_bits, board_size)
        )

    def _has_open_three_window_bits(self, current_bits, other_bits, board_size):
        line_windows = self._get_line_windows(board_size)

        for mask, _ in line_windows:
            my_count = (current_bits & mask).bit_count()
            opp_count = (other_bits & mask).bit_count()

            if opp_count == 0 and my_count >= 3:
                return True
            if my_count == 0 and opp_count >= 3:
                return True

        return False

    # ------------------------------------------------------------------
    # Immediate win targets / reachability
    # ------------------------------------------------------------------

    def _get_immediate_win_targets_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        board_size
    ):
        key = ("win_targets_bits", current_bits, other_bits)
        cached = self._tactical_cache.get(key)
        if cached is not None:
            self._prof_inc("win_targets_cache_hits")
            return cached

        self._prof_inc("win_targets_cache_misses")

        target_to_movers = self._get_target_to_movers_bits(
            current_bits, current_positions, other_bits, board_size
        )
        windows_by_sq = self._get_windows_by_sq(board_size)

        result_mask = 0

        for target_sq, movers_mask in target_to_movers.items():
            for _, other_mask in windows_by_sq[target_sq]:
                if (current_bits & other_mask) != other_mask:
                    continue

                if movers_mask & ~other_mask:
                    result_mask |= (1 << target_sq)
                    break

        self._tactical_cache[key] = result_mask
        return result_mask

    def _get_target_to_movers_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        board_size
    ):
        key = ("target_to_movers", current_bits, other_bits)
        cached = self._tactical_cache.get(key)
        if cached is not None:
            self._prof_inc("target_to_movers_cache_hits")
            return cached

        self._prof_inc("target_to_movers_cache_misses")

        occ_bits = current_bits | other_bits
        target_to_movers = {}

        for from_sq in current_positions:
            from_mask = 1 << from_sq
            moves = self._get_cached_available_moves_bits(occ_bits, from_sq, board_size)

            for target_sq in moves:
                target_to_movers[target_sq] = target_to_movers.get(target_sq, 0) | from_mask

        self._tactical_cache[key] = target_to_movers
        return target_to_movers

    def _get_reachable_targets_mask_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        board_size
    ):
        key = ("reachmask_bits", current_bits, other_bits)
        cached = self._tactical_cache.get(key)
        if cached is not None:
            self._prof_inc("reachmask_cache_hits")
            return cached

        self._prof_inc("reachmask_cache_misses")

        target_to_movers = self._get_target_to_movers_bits(
            current_bits, current_positions, other_bits, board_size
        )

        mask = 0
        for target_sq in target_to_movers.keys():
            mask |= (1 << target_sq)

        self._tactical_cache[key] = mask
        return mask

    def _get_moves_to_target_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        target_sq,
        board_size
    ):
        target_to_movers = self._get_target_to_movers_bits(
            current_bits, current_positions, other_bits, board_size
        )
        movers_mask = target_to_movers.get(target_sq, 0)
        return [(from_sq, target_sq) for from_sq in self._iter_bits(movers_mask)]

    # ------------------------------------------------------------------
    # Legal moves
    # ------------------------------------------------------------------

    def _get_all_legal_moves_bits(
        self,
        current_bits,
        current_positions,
        other_bits,
        board_size
    ):
        key = ("all_legal_moves_bits", current_bits, other_bits)
        cached = self._tactical_cache.get(key)
        if cached is not None:
            self._prof_inc("all_legal_moves_cache_hits")
            return cached

        self._prof_inc("all_legal_moves_cache_misses")

        occ_bits = current_bits | other_bits
        moves = []

        for from_sq in current_positions:
            available = self._get_cached_available_moves_bits(occ_bits, from_sq, board_size)
            for to_sq in available:
                moves.append((from_sq, to_sq))

        self._tactical_cache[key] = moves
        return moves

    # ------------------------------------------------------------------
    # Move generation
    # ------------------------------------------------------------------

    def _get_cached_available_moves_bits(self, occ_bits, sq, board_size):
        key = ("moves_bits", occ_bits, sq)
        cached = self._move_cache.get(key)
        if cached is not None:
            self._prof_inc("move_cache_hits")
            return cached

        self._prof_inc("move_cache_misses")
        moves = tuple(self._fast_available_moves_bits(occ_bits, sq, board_size))
        self._move_cache[key] = moves
        return moves

    def _fast_available_moves_bits(self, occ_bits, sq, board_size):
        moves = []
        rays = self._rays_cache[board_size][sq]

        for ray in rays:
            for target_sq in ray:
                if occ_bits & (1 << target_sq):
                    break
                moves.append(target_sq)

        return moves

    # ------------------------------------------------------------------
    # Bit helpers
    # ------------------------------------------------------------------

    def _iter_bits(self, bits):
        while bits:
            lsb = bits & -bits
            yield lsb.bit_length() - 1
            bits ^= lsb

    def _first_bit(self, bits):
        if bits == 0:
            return None
        return (bits & -bits).bit_length() - 1

    # ------------------------------------------------------------------
    # Apply / replace / win
    # ------------------------------------------------------------------

    def _apply_move_bits(self, bits, positions, from_sq, to_sq):
        new_bits = bits ^ (1 << from_sq) ^ (1 << to_sq)
        new_positions = self._replace_sq_in_positions(positions, from_sq, to_sq)
        return new_bits, new_positions

    def _replace_sq_in_positions(self, positions, from_sq, to_sq):
        lst = list(positions)
        idx = lst.index(from_sq)
        lst.pop(idx)
        bisect.insort(lst, to_sq)
        return tuple(lst)

    def _is_win_after_move_bits(self, bits, to_sq, board_size):
        for full_mask, _ in self._get_windows_by_sq(board_size)[to_sq]:
            if (bits & full_mask) == full_mask:
                return True
        return False

    # ------------------------------------------------------------------
    # Board conversion
    # ------------------------------------------------------------------

    def _board_to_bitboards(self, board, board_size):
        white_bits = 0
        black_bits = 0
        white_positions = []
        black_positions = []

        for r in range(board_size):
            for c in range(board_size):
                sq = self._rc_to_sq(r, c, board_size)
                cell = board[r][c]
                if cell == PieceType.WHITE:
                    white_bits |= (1 << sq)
                    white_positions.append(sq)
                elif cell == PieceType.BLACK:
                    black_bits |= (1 << sq)
                    black_positions.append(sq)

        return white_bits, black_bits, tuple(sorted(white_positions)), tuple(sorted(black_positions))

    def _rc_to_sq(self, r, c, board_size):
        if board_size not in self._rc_to_sq_cache:
            self._rc_to_sq_cache[board_size] = {
                (rr, cc): rr * board_size + cc
                for rr in range(board_size)
                for cc in range(board_size)
            }
        return self._rc_to_sq_cache[board_size][(r, c)]

    def _sq_to_rc(self, sq, board_size):
        if board_size not in self._sq_to_rc_cache:
            self._sq_to_rc_cache[board_size] = {
                rr * board_size + cc: (rr, cc)
                for rr in range(board_size)
                for cc in range(board_size)
            }
        return self._sq_to_rc_cache[board_size][sq]

    # ------------------------------------------------------------------
    # Geometry / precompute
    # ------------------------------------------------------------------

    def _ensure_precomputed(self, board_size):
        if board_size not in self._rays_cache:
            self._rays_cache[board_size] = self._build_rays_bits(board_size)

        cache_key = (board_size, WIN_CONDITION)
        if cache_key not in self._line_cache:
            self._get_line_windows(board_size)

        if cache_key not in self._windows_by_sq_cache:
            self._get_windows_by_sq(board_size)

    def _build_rays_bits(self, board_size):
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (-1, 1), (1, -1), (-1, -1), (1, 1),
        ]
        rays = {}
        for r in range(board_size):
            for c in range(board_size):
                sq = self._rc_to_sq(r, c, board_size)
                piece_rays = []
                for dr, dc in directions:
                    ray = []
                    rr, cc = r + dr, c + dc
                    while 0 <= rr < board_size and 0 <= cc < board_size:
                        ray.append(self._rc_to_sq(rr, cc, board_size))
                        rr += dr
                        cc += dc
                    piece_rays.append(ray)
                rays[sq] = piece_rays
        return rays

    def _get_line_windows(self, board_size):
        cache_key = (board_size, WIN_CONDITION)
        if cache_key in self._line_cache:
            return self._line_cache[cache_key]

        windows = []

        for r in range(board_size):
            for c in range(board_size - WIN_CONDITION + 1):
                sqs = tuple(self._rc_to_sq(r, c + i, board_size) for i in range(WIN_CONDITION))
                mask = 0
                for sq in sqs:
                    mask |= (1 << sq)
                windows.append((mask, sqs))

        for c in range(board_size):
            for r in range(board_size - WIN_CONDITION + 1):
                sqs = tuple(self._rc_to_sq(r + i, c, board_size) for i in range(WIN_CONDITION))
                mask = 0
                for sq in sqs:
                    mask |= (1 << sq)
                windows.append((mask, sqs))

        for r in range(board_size - WIN_CONDITION + 1):
            for c in range(board_size - WIN_CONDITION + 1):
                sqs = tuple(self._rc_to_sq(r + i, c + i, board_size) for i in range(WIN_CONDITION))
                mask = 0
                for sq in sqs:
                    mask |= (1 << sq)
                windows.append((mask, sqs))

        for r in range(board_size - WIN_CONDITION + 1):
            for c in range(WIN_CONDITION - 1, board_size):
                sqs = tuple(self._rc_to_sq(r + i, c - i, board_size) for i in range(WIN_CONDITION))
                mask = 0
                for sq in sqs:
                    mask |= (1 << sq)
                windows.append((mask, sqs))

        self._line_cache[cache_key] = windows
        return windows

    def _get_windows_by_sq(self, board_size):
        cache_key = (board_size, WIN_CONDITION)
        cached = self._windows_by_sq_cache.get(cache_key)
        if cached is not None:
            return cached

        mapping = {sq: [] for sq in range(board_size * board_size)}
        for full_mask, sqs in self._get_line_windows(board_size):
            for target_sq in sqs:
                other_mask = full_mask & ~(1 << target_sq)
                mapping[target_sq].append((full_mask, other_mask))

        self._windows_by_sq_cache[cache_key] = mapping
        return mapping