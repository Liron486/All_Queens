from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QApplication
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from utils import PieceType, BLACK_PIECE_PATH, WHITE_PIECE_PATH

class Cell(QLabel):
    clicked = pyqtSignal(int, int)  # Signal to emit when the cell is clicked

    def __init__(self, row, col, color, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.cell_default_color = color
        self.cell_color = color
        self.piece = PieceType.EMPTY  # No piece initially
        self.init_ui()

    def init_ui(self):
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.row, self.col)  # Emit the clicked signal with row and column

    def reset_cell(self):
        self.cell_color = self.cell_default_color
        self.setStyleSheet(f"background-color: {self.cell_color}; border: 1px solid black;")
    
    def cell_pressed(self):
        self.cell_color = "#d9f4fc"
        self.setStyleSheet(f"background-color: {self.cell_color}; border: 1px solid black;")

    def cell_available(self):
        border_width = self.get_scaled_border_width()
        self.setStyleSheet(f"background-color: {self.cell_color}; border: {border_width} solid #f79b07;")

    def cell_in_route(self):
        self.cell_color = self.adjust_color(self.cell_color)
        self.setStyleSheet(f"background-color: {self.cell_color}; border: 1px solid black;")

    def adjust_color(self, hex_color):
        if isinstance(hex_color, str):
            # Convert hex color to RGB
            hex_color = hex_color.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            
            if r > 127:
                # Increase r and g by 40% and decrease b by 20%
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

    def get_scaled_border_width(self):
        app = QApplication.instance() or QApplication([])
        screen = app.primaryScreen()
        logical_dpi = screen.logicalDotsPerInch()
        scaling_factor = ((logical_dpi / 240) ** 0.1) * 0.7
        return int(3 * scaling_factor)

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

    def get_piece_type(self):
        return self.piece
