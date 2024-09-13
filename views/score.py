from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap, QPalette, QFont
from PyQt5.QtCore import Qt
from utils import create_spacer_widget, PlayerType, DEFAULT_FONT

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
        self._player_name = player.name
        self._type = player.player_type
        self._difficulty = player.difficulty
        self._score = player.score
        self._move_num = player.move_number
        self._pic_path = player.piece_path
        self._pixmap = QPixmap(self._pic_path)
        self._init_ui()

    def update_score(self, player):
        """
        Updates the score and move number of the player in the UI.

        Args:
            player (Player): The player whose score and move number will be updated.
        """
        self._score = player.score
        self._move_num = player.move_number
        self._score_label.setText(f"{self._score}")
        move_num_text = f"Move no. {self._move_num}"
        self.player_info.setText(f"{self.player_info_text}<br>{move_num_text}")

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
        self.name_label = QLabel(self._player_name)
        self.name_label.setStyleSheet("color: black; font-weight: bold;")
        self.name_label.setFont(QFont(DEFAULT_FONT, 13))
        self.name_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        player_info_layout.addWidget(self.name_label)

        # Player info and move number combined text
        if self._type == PlayerType.HUMAN:
            self.player_info_text = "Human"
        else:
            self.player_info_text = f"AI, {self._difficulty}"

        move_num_text = f"Move no. {self._move_num}"
        combined_text = f"{self.player_info_text}<br>{move_num_text}"

        self.player_info = QLabel(combined_text)
        self.player_info.setStyleSheet("color: black;")
        self.player_info.setFont(QFont(DEFAULT_FONT, 10))
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
        self._score_label = QLabel(f"{self._score}")
        self._score_label.setStyleSheet("color: black; font-weight: bold;")
        self._score_label.setFont(QFont(DEFAULT_FONT, 16)) 
        self._score_label.setAlignment(Qt.AlignCenter)
        return self._score_label

    def _update_pixmap(self):
        """
        Updates the piece icon's pixmap to fit within the label.
        """
        if not self._pixmap.isNull():
            new_size = self.piece_label.size() * 0.4
            if new_size.width() > 0 and new_size.height() > 0:
                scaled_pixmap = self._pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        self._game_number = game_number
        self._init_ui()

    def update_game_number(self, game_number):
        """
        Updates the displayed game number.

        Args:
            game_number (int): The new game number to display.
        """
        self._game_number = game_number
        self._game_number_display.setText(str(self._game_number))

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
        self._game_number_label = QLabel("Game Number")
        self._game_number_label.setStyleSheet("color: black; font-weight: bold; text-decoration: underline;")
        self._game_number_label.setFont(QFont(DEFAULT_FONT, 14))
        return self._game_number_label

    def _create_game_number_label(self):
        """
        Creates the label displaying the current game number.

        Returns:
            QLabel: The label for the game number.
        """
        self._game_number_display = QLabel(str(self._game_number))
        self._game_number_display.setStyleSheet("color: black; font-weight: bold;")
        self._game_number_display.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self._game_number_display.setFont(QFont(DEFAULT_FONT, 18))
        return self._game_number_display


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
        self._player1_score = None
        self._player2_score = None
        self._player1_data = players[0]
        self._player2_data = players[1]
        self._game_number = game_number
        self._init_ui()

    def update_scores(self, players_data):
        """
        Updates the score displays for both players.

        Args:
            players_data (list): The updated player data for both players.
        """
        self._player1_score.update_score(players_data[0])
        self._player2_score.update_score(players_data[1])

    def update_game_number(self, game_number):
        """
        Updates the displayed game number.

        Args:
            game_number (int): The new game number to display.
        """
        self._game_number_module.update_game_number(game_number)

    def _init_ui(self):
        """
        Initializes the UI components for the Score widget.
        """
        layout = QHBoxLayout()

        self._player1_score = ScoreModule(self._player1_data)
        self._player2_score = ScoreModule(self._player2_data)
        self._game_number_module = GameNumberModule(self._game_number)

        layout.addWidget(self._player1_score)
        layout.addWidget(self._game_number_module)
        layout.addWidget(create_spacer_widget(self.width() * 0.078, self.height() * 0.1))
        layout.addWidget(self._player2_score)

        self.setStyleSheet("border: 0px solid black;")
        self.setLayout(layout)
