from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy
from views.cell import Cell
from utils import PieceType

class Board(QWidget):
    color1 = "#faeec0"  
    color2 = "#389661"

    def __init__(self, board, parent=None):
        super().__init__(parent)
        self.board_size = len(board)
        self.cells = {}
        self.init_ui(board)

    def init_ui(self, board):
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.init_board_background()
        self.init_board(board)

    def handle_cell_click(self, row, col):
        # Handle cell click event
        print(f"Cell clicked at ({row}, {col})")  # Replace with actual logic

    def init_board(self, board):
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.cells[(row, col)].set_cell_content(board[row][col])

    def init_board_background(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = self.color1 if (row + col) % 2 == 0 else self.color2
                cell = Cell(row, col, color)
                cell.clicked.connect(self.handle_cell_click)
                self.grid_layout.addWidget(cell, row, col)
                self.cells[(row, col)] = cell

