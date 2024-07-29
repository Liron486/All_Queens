from PyQt5.QtWidgets import QWidget, QGridLayout, QSizePolicy
from PyQt5.QtCore import pyqtSignal
from views.cell import Cell
from utils import PieceType

class Board(QWidget):
    cell_clicked = pyqtSignal(int, int)
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

    def set_cell_content(self, cell, piece_type):
        self.cells[cell].set_cell_content(piece_type)

    def get_cell_piece_type(self, cell):
        return self.cells[cell].get_piece_type()

    def reset_cells_view(self, cells_to_reset):
        for cell in cells_to_reset:
            self.cells[cell].reset_cell()

    def tag_cells_in_route(self, cells_in_route):
        for cell in cells_in_route:
            self.cells[cell].cell_in_route()

    def tag_available_cells(self, pressed_cell, available_cells):
        self.cells[pressed_cell].cell_pressed()
        for cell in available_cells:
            self.cells[cell].cell_available()

    def handle_cell_click(self, row, col):
        self.cell_clicked.emit(row, col)

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

