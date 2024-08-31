from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap, QPalette, QFont
from PyQt5.QtCore import Qt
from utils import create_spacer_widget, PlayerType

class ScoreModule(QWidget):
    """
    Represents a module displaying a player's score, move number, and piece icon.
    """

    def __init__(self, player, parent=None):
        """
        Initializes the ScoreModule with the provided player data.

        Args:
            player (Player): The player whose score and details will be displayed.
            parent (QWidget, optional): The parent widget, if any.
        """
        super().__init__(parent)
        self.player_name = player.get_name()
        self.type = player.get_player_type()
        self.difficulty = player.get_difficulty()
        self.score = player.get_score()
        self.move_num = player.get_move_number()
        self.pic_path = player.get_piece_path()
        self.pixmap = QPixmap(self.pic_path)
        self._init_ui()

    def update_score(self, player):
        """
        Updates the score and move number of the player in the UI.

        Args:
            player (Player): The player whose score and move number will be updated.
        """
        self.score = player.get_score()
        self.move_num = player.get_move_number()
        self.score_label.setText(f"{self.score}")
        move_num_text = f"Move no. {self.move_num}"
        self.player_info.setText(f"{self.player_info_text}<br>{move_num_text}")

    def set_background_color(self, color):
        """
        Sets the background color of the module.

        Args:
            color (QColor): The color to set as the background.
        """
        palette = self.palette()
        palette.setColor(QPalette.Background, color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def resizeEvent(self, event):
        """
        Handles the resize event, updating the piece icon to fit the new size.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        self._update_pixmap()

    def _init_ui(self):
        """
        Initializes the UI components for the ScoreModule.
        """
        layout = QHBoxLayout() 
        layout.addLayout(self._create_player_info_label())
        layout.addWidget(create_spacer_widget(self.width() * 0.015, self.height() * 0.02))
        layout.addWidget(self._create_score_label())
        layout.addWidget(self._create_piece_pic())

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _create_player_info_label(self):
        """
        Creates the label displaying the player's name, type, and move number.

        Returns:
            QVBoxLayout: The layout containing the player's information labels.
        """
        player_info_layout = QVBoxLayout()

        # Player name label
        self.name_label = QLabel(self.player_name)
        self.name_label.setStyleSheet("color: black; font-weight: bold;")
        self.name_label.setFont(QFont('Arial', 13))
        self.name_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        player_info_layout.addWidget(self.name_label)

        # Player info and move number combined text
        if self.type == PlayerType.HUMAN:
            self.player_info_text = "Human"
        else:
            self.player_info_text = f"AI, {self.difficulty}"

        move_num_text = f"Move no. {self.move_num}"
        combined_text = f"{self.player_info_text}<br>{move_num_text}"

        self.player_info = QLabel(combined_text)
        self.player_info.setStyleSheet("color: black;")
        self.player_info.setFont(QFont('Arial', 10))
        self.player_info.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        player_info_layout.addWidget(self.player_info)

        return player_info_layout

    def _create_piece_pic(self):
        """
        Creates the label displaying the piece icon.

        Returns:
            QLabel: The label for the piece icon.
        """
        self.piece_label = QLabel(self)
        self.piece_label.setAlignment(Qt.AlignCenter)
        self.piece_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return self.piece_label

    def _create_score_label(self):
        """
        Creates the label displaying the player's score.

        Returns:
            QLabel: The label for the score.
        """
        self.score_label = QLabel(f"{self.score}")
        self.score_label.setStyleSheet("color: black; font-weight: bold;")
        self.score_label.setFont(QFont('Arial', 16)) 
        self.score_label.setAlignment(Qt.AlignCenter)
        return self.score_label

    def _update_pixmap(self):
        """
        Updates the piece icon's pixmap to fit within the label.
        """
        if not self.pixmap.isNull():
            new_size = self.piece_label.size() * 0.4
            if new_size.width() > 0 and new_size.height() > 0:
                scaled_pixmap = self.pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.piece_label.setPixmap(scaled_pixmap)


class GameNumberModule(QWidget):
    """
    Represents a module displaying the current game number.
    """

    def __init__(self, game_number, parent=None):
        """
        Initializes the GameNumberModule with the provided game number.

        Args:
            game_number (int): The current game number.
            parent (QWidget, optional): The parent widget, if any.
        """
        super().__init__(parent)
        self.game_number = game_number
        self._init_ui()

    def update_game_number(self, game_number):
        """
        Updates the displayed game number.

        Args:
            game_number (int): The new game number to display.
        """
        self.game_number = game_number
        self.game_number_display.setText(str(self.game_number))

    def _init_ui(self):
        """
        Initializes the UI components for the GameNumberModule.
        """
        layout = QVBoxLayout()
        layout.addWidget(self._create_label())
        layout.addWidget(self._create_game_number_label())
        self.setLayout(layout)

    def _create_label(self):
        """
        Creates the label for the "Game Number" text.

        Returns:
            QLabel: The label for the "Game Number" text.
        """
        self.game_number_label = QLabel("Game Number")
        self.game_number_label.setStyleSheet("color: black; font-weight: bold; text-decoration: underline;")
        self.game_number_label.setFont(QFont('Arial', 14))
        return self.game_number_label

    def _create_game_number_label(self):
        """
        Creates the label displaying the current game number.

        Returns:
            QLabel: The label for the game number.
        """
        self.game_number_display = QLabel(str(self.game_number))
        self.game_number_display.setStyleSheet("color: black; font-weight: bold;")
        self.game_number_display.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.game_number_display.setFont(QFont('Arial', 18))
        return self.game_number_display


class Score(QWidget):
    """
    Represents the score display for two players and the game number in a game.
    """

    def __init__(self, players, game_number, parent=None):
        """
        Initializes the Score widget with the provided players and game number.

        Args:
            players (list): List of players participating in the game.
            game_number (int): The current game number.
            parent (QWidget, optional): The parent widget, if any.
        """
        super().__init__(parent)
        self.player1_data = players[0]
        self.player2_data = players[1]
        self.game_number = game_number
        self._init_ui()

    def update_scores(self, players_data):
        """
        Updates the score displays for both players.

        Args:
            players_data (list): The updated player data for both players.
        """
        self.player1_score.update_score(players_data[0])
        self.player2_score.update_score(players_data[1])

    def update_game_number(self, game_number):
        """
        Updates the displayed game number.

        Args:
            game_number (int): The new game number to display.
        """
        self.game_number_module.update_game_number(game_number)

    def _init_ui(self):
        """
        Initializes the UI components for the Score widget.
        """
        layout = QHBoxLayout()

        self.player1_score = ScoreModule(self.player1_data)
        self.player2_score = ScoreModule(self.player2_data)
        self.game_number_module = GameNumberModule(self.game_number)

        layout.addWidget(self.player1_score)
        layout.addWidget(self.game_number_module)
        layout.addWidget(create_spacer_widget(self.width() * 0.078, self.height() * 0.1))
        layout.addWidget(self.player2_score)

        self.setStyleSheet("border: 0px solid black;")
        self.setLayout(layout)
