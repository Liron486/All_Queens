from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy
from views.cell import Cell, PieceType  # Make sure this import is correct based on your project structure

class Board(QWidget):
    color1 = "#FFF8DC"  
    color2 = "#b7653a"

    def __init__(self, size=5, parent=None):
        super().__init__(parent)
        self.size = size
        self.init_ui()

    def init_ui(self):
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.init_board_ui()
        self.init_board_pieces()

    def handle_cell_click(self, row, col):
        # Handle cell click event
        print(f"Cell clicked at ({row}, {col})")  # Replace with actual logic

    def update_board(self, board):
        for row in range(self.size):
            for col in range(self.size):
                self.cells[(row, col)].update_cell(board[row][col])

    def init_board_ui(self):
        self.cells = {}
        for row in range(self.size):
            for col in range(self.size):
                color = self.color1 if (row + col) % 2 == 0 else self.color2
                cell = Cell(row, col, color)
                cell.clicked.connect(self.handle_cell_click)
                self.grid_layout.addWidget(cell, row, col)
                self.cells[(row, col)] = cell

    def init_board_pieces(self):
        self.cells[(0,0)].set_cell_content(PieceType.WHITE)
        self.cells[(0,1)].set_cell_content(PieceType.BLACK)
        self.cells[(1,0)].set_cell_content(PieceType.WHITE)
        self.cells[(1,1)].set_cell_content(PieceType.BLACK)
