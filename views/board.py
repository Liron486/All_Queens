from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy
from views.cell import Cell
from utils import PieceType

class Board(QWidget):
    color1 = "#FFF8DC"  
    color2 = "#389661"

    def __init__(self, size=5, parent=None):
        super().__init__(parent)
        self.size = size
        self.cells = {}
        self.init_ui()

    def init_ui(self):
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.init_board_ui()

    def handle_cell_click(self, row, col):
        # Handle cell click event
        print(f"Cell clicked at ({row}, {col})")  # Replace with actual logic

    def update_board(self, board):
        for row in range(self.size):
            for col in range(self.size):
                self.cells[(row, col)].set_cell_content(board[row][col])

    def init_board_ui(self):
        for row in range(self.size):
            for col in range(self.size):
                color = self.color1 if (row + col) % 2 == 0 else self.color2
                cell = Cell(row, col, color)
                cell.clicked.connect(self.handle_cell_click)
                self.grid_layout.addWidget(cell, row, col)
                self.cells[(row, col)] = cell

