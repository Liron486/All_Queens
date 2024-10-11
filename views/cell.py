from PyQt5.QtWidgets import QLabel, QSizePolicy, QApplication
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from utils import PieceType, BLACK_PIECE_PATH, WHITE_PIECE_PATH

class Cell(QLabel):
    """
    Represents a single cell on a board, handling its appearance, interactions,
    and the piece it contains.
    """
    
    clicked = pyqtSignal(int, int)  # Signal emitted when the cell is clicked

    def __init__(self, row, col, color, label_texts=None, parent=None):
        """
        Initializes the Cell with the given row, column, background color, and optional labels.

        Args:
            row (int): The row index of the cell.
            col (int): The column index of the cell.
            color (str): The default background color of the cell.
            label_texts (list of tuples, optional): A list of tuples (text, alignment) for labels.
            parent (QWidget, optional): The parent widget, if any.
        """
        super().__init__(parent)
        self.setObjectName('Cell')  # Set object name for stylesheet targeting
        self._row = row
        self._col = col
        self._cell_default_color = color
        self._cell_color = color
        self._piece = PieceType.EMPTY  # No piece initially
        self._label_texts = label_texts or []  # Store label texts and alignments
        self._init_ui()

    def reset_cell(self):
        """
        Resets the cell to its default state, including color and border.
        """
        self._cell_color = self._cell_default_color
        self.setStyleSheet(f"""
            #{self.objectName()} {{
                background-color: {self._cell_color};
                border: 1px solid black;
            }}
        """)

    def cell_pressed(self):
        """
        Changes the cell's appearance to indicate it has been pressed.
        """
        self._cell_color = "#d9f4fc"
        self.setStyleSheet(f"""
            #{self.objectName()} {{
                background-color: {self._cell_color};
                border: 1px solid black;
            }}
        """)

    def cell_available(self):
        """
        Highlights the cell to indicate it is available for a move.
        """
        border_width = self._get_border_width()
        self.setStyleSheet(f"""
            #{self.objectName()} {{
                background-color: {self._cell_color};
                border: {border_width}px solid #f79b07;
            }}
        """)

    def cell_in_route(self):
        """
        Changes the cell's color to indicate it is part of a route.
        """
        self._cell_color = self._adjust_color(self._cell_default_color)
        self.setStyleSheet(f"""
            #{self.objectName()} {{
                background-color: {self._cell_color};
                border: 1px solid black;
            }}
        """)

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
        self._update_cell_content()
        self._image_label.setGeometry(0, 0, self.width(), self.height())
        self._update_label_positions()

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
        self._update_cell_content()

    def _init_ui(self):
        """
        Initializes the UI for the cell, including setting up the image and text labels.
        """
        self.reset_cell()
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Configure the _image_label to fill the entire cell
        self._image_label = QLabel(self)
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._image_label.setGeometry(0, 0, self.width(), self.height())
        
        # Create labels for each label_text in label_texts
        self._labels = []
        for text, alignment in self._label_texts:
            label = QLabel(self)
            label.setText(text)
            label.setStyleSheet("color: black; background: transparent; border: none;")  # No border or background
            label.setAlignment(alignment)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            label.setAttribute(Qt.WA_TransparentForMouseEvents)  # Allow clicks to pass through
            self._labels.append(label)

    def _update_label_positions(self):
        """
        Updates the positions and font sizes of the labels within the cell.
        """
        margin = max(2, int(self.width() * 0.05))
        font_size = self._get_label_size()
        for label in self._labels:
            font = label.font()
            font.setPointSize(font_size)
            label.setFont(font)

            text_width = label.sizeHint().width()
            text_height = label.sizeHint().height()
            alignment = label.alignment()
            if alignment == (Qt.AlignBottom | Qt.AlignRight):
                x = self.width() - text_width - margin
                y = self.height() - text_height - margin
            elif alignment == (Qt.AlignTop | Qt.AlignLeft):
                x = margin
                y = margin
            else:
                x = (self.width() - text_width) / 2
                y = (self.height() - text_height) / 2
            label.move(int(x), int(y))
            label.raise_()  # Ensure the label is above other widgets

    def _update_cell_content(self):
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
            self._image_label.setPixmap(scaled_pixmap)
        else:
            self._image_label.clear()

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
                # Changing the yellow color
                r,g,b = 252,241,109
            else:
                # Changing the green color
                r,g,b = 52,199,50

            # Convert back to hex
            new_color = f'#{r:02x}{g:02x}{b:02x}'
            return new_color
        else:
            raise ValueError("Provided color is not a valid hex string")

    def _calculate_scaled_value(self, divisor: float, exponent: float, multiplier: float) -> int:
        """
        Helper method to calculate a scaled value based on the screen's DPI.

        Args:
            divisor (float): The value by which the DPI is divided.
            exponent (float): The exponent to which the scaled DPI is raised.
            multiplier (float): The multiplier applied after scaling.

        Returns:
            int: The calculated scaled value.
        """
        app = QApplication.instance() or QApplication([])
        screen = app.primaryScreen()
        logical_dpi = screen.logicalDotsPerInch()
        scaling_factor = ((logical_dpi / divisor) ** exponent) * multiplier
        return int(scaling_factor)

    def _get_label_size(self) -> int:
        """
        Calculates a scaled font size based on the cell's height.

        Returns:
            int: The scaled font size.
        """
        return self._calculate_scaled_value(divisor=80, exponent=0.15, multiplier=9.5)

    def _get_border_width(self) -> int:
        """
        Calculates a scaled border width based on the screen's DPI.

        Returns:
            int: The scaled border width in pixels.
        """
        return self._calculate_scaled_value(divisor=100, exponent=0.75, multiplier=6)
