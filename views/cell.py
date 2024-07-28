from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from utils import PieceType, BLACK_PIECE_PATH, WHITE_PIECE_PATH

class Cell(QLabel):
    clicked = pyqtSignal(int, int)  # Signal to emit when the cell is clicked

    def __init__(self, row, col, color, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.color = color
        self.piece = PieceType.EMPTY  # No piece initially
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {self.color}; border: 1px solid black;")
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.row, self.col)  # Emit the clicked signal with row and column

    def update_cell(self):
        if self.piece == PieceType.WHITE:
            pixmap = QPixmap(WHITE_PIECE_PATH)
        elif self.piece == PieceType.BLACK:
            pixmap = QPixmap(BLACK_PIECE_PATH)
        else:
            pixmap = None

        if pixmap:
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.clear()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_cell()

    def set_cell_content(self, piece_type):
        self.piece = piece_type
        self.update_cell()
