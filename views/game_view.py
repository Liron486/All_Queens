from PyQt5.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from views.board import Board
from views.score import Score
from utils import BackgroundWindow, PieceType, resource_path, DEFAULT_FONT
from logger import get_logger

GAME_BACKGROUND_IMAGE_PATH = resource_path('resources/images/game_background.png')

B_KEY_HEBREW_VALUE = 1504
P_KEY_HEBREW_VALUE = 1508

class GameWindow(BackgroundWindow):
    """
    Represents the main game window, handling the board, score, and game interactions.
    """
    
    exit_full_screen_signal = pyqtSignal()
    key_pressed_signal = pyqtSignal()
    b_key_was_pressed_signal = pyqtSignal()
    p_key_was_pressed_signal = pyqtSignal()
    player_make_move_signal = pyqtSignal(int, int)

    def __init__(self, players, game_number, board, parent=None):
        """
        Initializes the GameWindow with the given players, game number, and board.

        Args:
            players (list): List of players participating in the game.
            game_number (int): The current game number.
            board (list): The initial board setup as a 2D list.
            parent (QWidget, optional): The parent widget, if any.
        """
        super().__init__(GAME_BACKGROUND_IMAGE_PATH, parent)
        self._logger = get_logger(self.__class__.__name__)
        self._init_ui(players, game_number, board)
        self._setup_connections()

    def tag_available_cells(self, pressed_cell, available_cells):
        """
        Highlights the available cells for a move on the board.

        Args:
            pressed_cell (tuple): The coordinates of the pressed cell.
            available_cells (list): List of available cells (as tuples) for the move.
        """
        self._board.tag_available_cells(pressed_cell, available_cells)

    def tag_cells_in_route(self, cells_in_route):
        """
        Marks the cells that are part of a move route.

        Args:
            cells_in_route (list): List of cells (as tuples) that are part of the move route.
        """
        self._board.tag_cells_in_route(cells_in_route)

    def reset_cells_view(self, cells_to_reset):
        """
        Resets the view of specified cells to their default state.

        Args:
            cells_to_reset (list): List of cells (as tuples) to reset.
        """
        self._board.reset_cells_view(cells_to_reset)

    def execute_move(self, move):
        """
        Executes a move on the board by updating the piece position.

        Args:
            move (dict): A dictionary containing the move details with 'from' and 'to' coordinates.
        """
        piece_type = self._board.get_cell_content(move["from"])
        self._board.set_cell_content(move["from"], PieceType.EMPTY)
        self._board.set_cell_content(move["to"], piece_type)

    def player_make_move(self, row, col):
        """
        Emits a signal when a player makes a move by clicking on the board.

        Args:
            row (int): The row index of the clicked cell.
            col (int): The column index of the clicked cell.
        """
        self.player_make_move_signal.emit(row, col)

    def keyPressEvent(self, event):
        """
        Handles key press events, emitting relevant signals based on the key pressed.

        Args:
            event (QKeyEvent): The key press event.
        """
        self._logger.debug(f"Key pressed - {event.key()}")

        # Dictionary to map key codes to corresponding signals
        key_code_actions = {
            Qt.Key_Escape: self.exit_full_screen_signal.emit,
            Qt.Key_B: self.b_key_was_pressed_signal.emit,
            B_KEY_HEBREW_VALUE: self.b_key_was_pressed_signal.emit,  # Hebrew B key
            Qt.Key_P: self.p_key_was_pressed_signal.emit,
            P_KEY_HEBREW_VALUE: self.p_key_was_pressed_signal.emit,  # Hebrew P key
        }

        action = key_code_actions.get(event.key())

        if action:
            action()
        else:
            self.key_pressed_signal.emit()


    def game_paused(self):
        """
        Displays the pause overlay to indicate that the game is paused.
        """
        self._pause_overlay.setVisible(True)

    def game_resumed(self):
        """
        Hides the pause overlay to indicate that the game has resumed.
        """
        self._pause_overlay.setVisible(False)

    def display_winning_text(self, winner):
        """
        Displays the winning text when a player wins the game.

        Args:
            winner (str): The name of the winning player.
        """
        self._winning_text.setText(f"We Have A Winner! {winner} Wins!")
        self._play_again_text.setText("Press any key to start a new game")

    def mousePressEvent(self, event):
        """
        Handles mouse press events, emitting a signal when the left button is pressed.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if event.button() == Qt.LeftButton:
            self.player_make_move_signal.emit(-1, -1)

    def start_new_game(self, board, players_data, cells_to_reset, game_number):
        """
        Resets the game state for a new game.

        Args:
            board (list): The new board setup as a 2D list.
            players_data (list): The updated player data.
            cells_to_reset (list): List of cells to reset.
            game_number (int): The new game number.
        """
        self.reset_cells_view(cells_to_reset)
        self._board.reset_board(board)
        self._score.update_scores(players_data)
        self._score.update_game_number(game_number)
        self._winning_text.setText("")
        self._play_again_text.setText("")

    def update_move_number(self, players_data):
        """
        Updates the score display with the current move number.

        Args:
            players_data (list): The current player data.
        """
        self._score.update_scores(players_data)

    def _setup_connections(self):
        """
        Sets up signal-slot connections for the board interactions.
        """
        self._board.cell_clicked.connect(self.player_make_move)

    def _init_ui(self, players, game_number, board):
        """
        Initializes the UI elements for the game window.

        Args:
            players (list): List of players participating in the game.
            game_number (int): The current game number.
            board (list): The initial board setup as a 2D list.
        """
        self.setWindowTitle('4 Queens')
        self._create_main_layout()

        # Create the score component
        self._score = Score(players, game_number)
        self._score.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._main_layout.addWidget(self._score, alignment=Qt.AlignTop | Qt.AlignHCenter)
        
        # Create the board component
        self._board = Board(board)
        self._board.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._main_layout.addWidget(self._board, alignment=Qt.AlignCenter)

        # Create winning text component
        self._winning_text = QLabel("")
        self._winning_text.setStyleSheet("color: black; font-weight: bold;")
        self._winning_text.setFont(QFont(DEFAULT_FONT, 18))
        self._winning_text.setAlignment(Qt.AlignCenter)
        self._winning_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self._main_layout.addWidget(self._winning_text)

        # Initialize the pause overlay
        self._pause_overlay = QLabel(self)
        self._pause_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 50);")
        self._pause_overlay.setVisible(False)  # Initially hidden

        # Create play again text component
        self._play_again_text = QLabel("")
        self._play_again_text.setStyleSheet("color: black;")
        self._play_again_text.setFont(QFont(DEFAULT_FONT, 10))
        self._play_again_text.setAlignment(Qt.AlignCenter)
        self._play_again_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self._main_layout.addWidget(self._play_again_text)

    def _create_main_layout(self):
        """
        Creates the main layout for the game window.
        """
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self._main_layout = QVBoxLayout(central_widget)
        self._main_layout.setAlignment(Qt.AlignTop)

    def resizeEvent(self, event):
        """
        Handles the resize event, adjusting UI elements as necessary.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        self._resize_elements()

    def _resize_elements(self):
        """
        Resizes and positions the elements within the game window based on the current size.
        """
        window_width = self.width()
        window_height = self.height()

        # Calculate the maximum size for the board and score
        max_board_size = min(window_width * 0.85, (window_height * 0.85) - (window_height * 0.2))
        self._board.setFixedSize(max_board_size, max_board_size)

        # Set the score width to match the board width and adjust height proportionally
        score_height = int(window_height * 0.2)
        self._score.setFixedSize(max_board_size, score_height)

        self._pause_overlay.setFixedSize(window_width, window_height)
