from PyQt5.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QHBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont
from views.board import Board
from views.score import Score
from utils import BackgroundWindow, PieceType, resource_path
from logger import get_logger

class GameWindow(BackgroundWindow):
    exit_full_screen_signal = pyqtSignal()
    key_pressed_signal = pyqtSignal()
    player_make_move_signal = pyqtSignal(int, int)

    def __init__(self, players, game_number, board, parent=None):
        super().__init__(resource_path('resources/images/game_background.png'), parent)
        self.logger = get_logger(self.__class__.__name__)
        self.init_ui(players, game_number, board)
        self.setup_connections()

    def setup_connections(self):
        self.board.cell_clicked.connect(self.player_make_move)

    def init_ui(self, players, game_number, board):
        self.setWindowTitle('4 Queens')
        self.create_main_layout()

        # Create the score component
        self.score = Score(players, game_number)
        self.score.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.main_layout.addWidget(self.score, alignment=Qt.AlignTop | Qt.AlignHCenter)
        
        # Create the board component
        self.board = Board(board)
        self.board.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.board, alignment=Qt.AlignCenter)

        # Create winning text component
        self.winning_text = QLabel("")
        self.winning_text.setStyleSheet("color: black; font-weight: bold;")
        self.winning_text.setFont(QFont('Arial', 18))
        self.winning_text.setAlignment(Qt.AlignCenter)
        self.winning_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.main_layout.addWidget(self.winning_text)

        # Create play again text component
        self.play_again_text = QLabel("")
        self.play_again_text.setStyleSheet("color: black;")
        self.play_again_text.setFont(QFont('Arial', 10))
        self.play_again_text.setAlignment(Qt.AlignCenter)
        self.play_again_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.main_layout.addWidget(self.play_again_text)

    def tag_available_cells(self, pressed_cell, available_cells):
        self.board.tag_available_cells(pressed_cell, available_cells)

    def tag_cells_in_route(self, cells_in_route):
        self.board.tag_cells_in_route(cells_in_route)

    def reset_cells_view(self, cells_to_reset):
        self.board.reset_cells_view(cells_to_reset)

    def execute_move(self, move):
        piece_type = self.board.get_cell_piece_type(move["from"])
        self.board.set_cell_content(move["from"], PieceType.EMPTY)
        self.board.set_cell_content(move["to"], piece_type)       

    def player_make_move(self, row, col):
        self.player_make_move_signal.emit(row, col)

    def keyPressEvent(self, event):
        self.logger.debug(f"Key pressed - {event.key()}")
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()
        else:
            self.key_pressed_signal.emit()

    def display_winning_text(self, winner):
        self.winning_text.setText(f"We Have A Winner! {winner} Wins!")
        self.play_again_text.setText("Press any key to start a new game")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.player_make_move_signal.emit(-1, -1)

    def start_new_game(self, board, players_data, cells_to_reset, game_number):
        self.reset_cells_view(cells_to_reset)
        self.board.reset_board(board)
        self.score.update_scores(players_data)
        self.score.update_game_number(game_number)
        self.winning_text.setText("")
        self.play_again_text.setText("")

    def create_main_layout(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setAlignment(Qt.AlignTop)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_board_and_score_size()

    def update_board_and_score_size(self):
        window_width = self.width()
        window_height = self.height()

        # Calculate the maximum size for the board and score
        max_board_size = min(window_width * 0.85, (window_height * 0.85) - (window_height * 0.2))
        self.board.setFixedSize(max_board_size, max_board_size)

        # Set the score width to match the board width and adjust height proportionally
        score_height = int(window_height * 0.2)
        self.score.setFixedSize(max_board_size, score_height)

        


