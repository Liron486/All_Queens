from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QApplication
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from utils import PieceType, BLACK_PIECE_PATH, WHITE_PIECE_PATH

class Cell(QLabel):
    """
    Represents a single cell on a board, handling its appearance, interactions,
    and the piece it contains.
    """
    
    clicked = pyqtSignal(int, int)  # Signal emitted when the cell is clicked

    def __init__(self, row, col, color, parent=None):
        """
        Initializes the Cell with the given row, column, and background color.

        Args:
            row (int): The row index of the cell.
            col (int): The column index of the cell.
            color (str): The default background color of the cell.
            parent (QWidget, optional): The parent widget, if any.
        """
        super().__init__(parent)
        self._row = row
        self._col = col
        self._cell_default_color = color
        self._cell_color = color
        self._piece = PieceType.EMPTY  # No piece initially
        self._init_ui()

    def reset_cell(self):
        """
        Resets the cell to its default state, including color and border.
        """
        self._cell_color = self._cell_default_color
        self.setStyleSheet(f"background-color: {self._cell_color}; border: 1px solid black;")
    
    def cell_pressed(self):
        """
        Changes the cell's appearance to indicate it has been pressed.
        """
        self._cell_color = "#d9f4fc"
        self.setStyleSheet(f"background-color: {self._cell_color}; border: 1px solid black;")

    def cell_available(self):
        """
        Highlights the cell to indicate it is available for a move.
        """
        border_width = self._get_scaled_border_width()
        self.setStyleSheet(f"background-color: {self._cell_color}; border: {border_width}px solid #f79b07;")

    def cell_in_route(self):
        """
        Changes the cell's color to indicate it is part of a route.
        """
        self._cell_color = self._adjust_color(self._cell_default_color)
        self.setStyleSheet(f"background-color: {self._cell_color}; border: 1px solid black;")

    def mousePressEvent(self, event):
        """
        Handles the mouse press event, emitting the clicked signal if the left button is pressed.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._row, self._col)  # Emit the clicked signal with row and column

    def resizeEvent(self, event):
        """
        Handles the resize event, updating the cell content to fit the new size.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        self._update_cell()

    @property
    def cell_content(self):
        """
        Retrieves the content of the cell, which is the type of piece it holds.

        Returns:
            PieceType: The type of piece in the cell.
        """
        return self._piece

    @cell_content.setter
    def cell_content(self, piece_type):
        """
        Sets the content of the cell, which determines the type of piece it holds.

        Args:
            piece_type (PieceType): The type of piece to place in the cell.
        """
        self._piece = piece_type
        self._update_cell()

    def _init_ui(self):
        """
        Initializes the UI for the cell, including setting up the layout and image label.
        """
        self.reset_cell()
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Configure the image_label
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a layout and add the image_label to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def _update_cell(self):
        """
        Updates the cell's content by adjusting the piece image to the current size of the cell.
        """
        if self._piece == PieceType.WHITE:
            pixmap = QPixmap(WHITE_PIECE_PATH)
        elif self._piece == PieceType.BLACK:
            pixmap = QPixmap(BLACK_PIECE_PATH)
        else:
            pixmap = None

        if pixmap:
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.clear()

    def _adjust_color(self, hex_color):
        """
        Adjusts the given color to create a visually distinct variation.

        Args:
            hex_color (str): The color in hex format.

        Returns:
            str: The adjusted color in hex format.
        """
        if isinstance(hex_color, str):
            # Convert hex color to RGB
            hex_color = hex_color.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            
            if r > 127:
                # Increase r by 50%, g by 40% and decrease b by 20%
                r = min(255, int(r * 1.5))
                g = min(255, int(g * 1.4))
                b = max(0, int(b * 0.8))
            else:
                # Decrease r and g by 5% and b by 60%
                r = max(0, int(r * 0.95))
                g = max(0, int(g * 0.95))
                b = max(0, int(b * 0.4))

            # Convert back to hex
            new_color = f'#{r:02x}{g:02x}{b:02x}'
            return new_color
        else:
            raise ValueError("Provided color is not a valid hex string")

    def _get_scaled_border_width(self):
        """
        Calculates a scaled border width based on the screen's DPI.

        Returns:
            int: The scaled border width in pixels.
        """
        app = QApplication.instance() or QApplication([])
        screen = app.primaryScreen()
        logical_dpi = screen.logicalDotsPerInch()
        scaling_factor = ((logical_dpi / 240) ** 0.1) * 0.7
        return int(3 * scaling_factor)
