from PyQt5.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from views.board import Board
from utils import BackgroundWindow
from logger import get_logger

class GameWindow(BackgroundWindow):
    exit_full_screen_signal = pyqtSignal()

    def __init__(self, board_size, parent=None):
        super().__init__('resources/images/game_background.png')
        self.logger = get_logger(self.__class__.__name__)
        self.init_ui(board_size)

    def init_ui(self, board_size):
        self.setWindowTitle('4 Queens')
        self.create_main_layout()

        self.board = Board(board_size)
        self.board.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.update_board_size()
        self.main_layout.addWidget(self.board, alignment=Qt.AlignCenter)

    def keyPressEvent(self, event):
        self.logger.debug(f"Key pressed - {event.key()}")
        if event.key() == Qt.Key_Escape:
            self.exit_full_screen_signal.emit()

    def create_main_layout(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setAlignment(Qt.AlignCenter)

    def update_view(self, game_state):
        self.board.update_board(game_state.get_board())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_board_size()

    def update_board_size(self):
        window_width = self.width()
        board_size = int(window_width * 0.4)
        self.board.setFixedSize(QSize(board_size, board_size))
