from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import pyqtSignal
from views.cell import Cell
from utils import PieceType

class Board(QWidget):
    """
    Represents a chess or game board, handling the UI and interactions for the board cells.
    """
    
    cell_clicked = pyqtSignal(int, int)  # Signal emitted when a cell is clicked
    color1 = "#faeec0"  # First color for the board cells
    color2 = "#389661"  # Second color for the board cells

    def __init__(self, board, parent=None):
        """
        Initializes the Board widget with the given board setup.

        Args:
            board (list): The initial setup of the board, a 2D list representing the pieces.
            parent (QWidget, optional): The parent widget, if any.
        """
        super().__init__(parent)
        self.board_size = len(board)
        self.cells = {}
        self._init_ui(board)

    def set_cell_content(self, cell, piece_type):
        """
        Sets the content of a specific cell on the board.

        Args:
            cell (tuple): The coordinates of the cell (row, col).
            piece_type (PieceType): The type of piece to place in the cell.
        """
        self.cells[cell].set_cell_content(piece_type)

    def get_cell_piece_type(self, cell):
        """
        Retrieves the type of piece currently in a specific cell.

        Args:
            cell (tuple): The coordinates of the cell (row, col).

        Returns:
            PieceType: The type of piece in the cell.
        """
        return self.cells[cell].get_piece_type()

    def reset_cells_view(self, cells_to_reset):
        """
        Resets the view of the specified cells to their default state.

        Args:
            cells_to_reset (list): A list of cells (as tuples) to reset.
        """
        for cell in cells_to_reset:
            self.cells[cell].reset_cell()

    def tag_cells_in_route(self, cells_in_route):
        """
        Marks the cells in a specified route.

        Args:
            cells_in_route (list): A list of cells (as tuples) that are part of the route.
        """
        for cell in cells_in_route:
            self.cells[cell].cell_in_route()

    def tag_available_cells(self, pressed_cell, available_cells):
        """
        Marks the available cells for a move, and highlights the pressed cell.

        Args:
            pressed_cell (tuple): The coordinates of the pressed cell.
            available_cells (list): A list of available cells (as tuples) for the move.
        """
        self.cells[pressed_cell].cell_pressed()
        for cell in available_cells:
            self.cells[cell].cell_available()

    def handle_cell_click(self, row, col):
        """
        Handles the event when a cell is clicked, emitting a signal with the cell's coordinates.

        Args:
            row (int): The row index of the clicked cell.
            col (int): The column index of the clicked cell.
        """
        self.cell_clicked.emit(row, col)

    def reset_board(self, board):
        """
        Resets the entire board to a new setup.

        Args:
            board (list): A 2D list representing the new setup of the board.
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.cells[(row, col)].set_cell_content(board[row][col])

    def _init_ui(self, board):
        """
        Initializes the UI of the board, setting up the layout and background.

        Args:
            board (list): The initial setup of the board.
        """
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self._init_board_background()
        self.reset_board(board)

    def _init_board_background(self):
        """
        Initializes the board background, creating cells with alternating colors.
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = self.color1 if (row + col) % 2 == 0 else self.color2
                cell = Cell(row, col, color)
                cell.clicked.connect(self.handle_cell_click)
                self.grid_layout.addWidget(cell, row, col)
                self.cells[(row, col)] = cell
