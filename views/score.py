from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap, QPalette, QFont
from PyQt5.QtCore import Qt
from utils import create_spacer_widget, PlayerType

class ScoreModule(QWidget):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player_name = player.get_name()
        self.type = player.get_player_type()
        self.difficulty = player.get_difficulty()
        self.score = player.get_score()
        self.pic_path = player.get_piece_path()
        self.pixmap = QPixmap(self.pic_path)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout() 
        layout.addLayout(self.create_player_info_label())
        layout.addWidget(create_spacer_widget(self.width() * 0.015, self.height() * 0.02))
        layout.addWidget(self.create_score_label())
        layout.addWidget(self.crete_piece_pic())

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def create_player_info_label(self):
        player_info_layout = QVBoxLayout()

        # Player name label
        self.name_label = QLabel(self.player_name)
        self.name_label.setStyleSheet("color: black; font-weight: bold;")
        self.name_label.setFont(QFont('Arial', 13))
        self.name_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        player_info_layout.addWidget(self.name_label)

        # Player info text
        if self.type == PlayerType.HUMAN:
            player_info_text = "Human"
        else:
            player_info_text = f"AI, {self.difficulty}"
        self.type_label = QLabel(player_info_text)
        self.type_label.setStyleSheet("color: black;")
        self.type_label.setFont(QFont('Arial', 10)) 
        self.type_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        player_info_layout.addWidget(self.type_label)

        return player_info_layout

    def crete_piece_pic(self):
        self.piece_label = QLabel(self)
        self.piece_label.setAlignment(Qt.AlignCenter)
        self.piece_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return self.piece_label

    def create_score_label(self):
        self.score_label = QLabel(f"{self.score}")
        self.score_label.setStyleSheet("color: black; font-weight: bold;")
        self.score_label.setFont(QFont('Arial', 16)) 
        self.score_label.setAlignment(Qt.AlignCenter)

        return self.score_label

    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Background, color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def update_score(self, player):
        self.score = player.get_score()
        self.score_label.setText(f"{self.score}")

    def update_pixmap(self):
        if not self.pixmap.isNull():
            new_size = self.piece_label.size() * 0.4
            if new_size.width() > 0 and new_size.height() > 0:
                scaled_pixmap = self.pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.piece_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()


class GameNumberModule(QWidget):
    def __init__(self, game_number, parent=None):
        super().__init__(parent)
        self.game_number = game_number
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.create_label())
        layout.addWidget(self.create_game_number_label())
        self.setLayout(layout)

    def create_label(self):
        self.game_number_label = QLabel("Game Number")
        self.game_number_label.setStyleSheet("color: black; font-weight: bold; text-decoration: underline;")
        self.game_number_label.setFont(QFont('Arial', 14))
        return self.game_number_label

    def create_game_number_label(self):
        self.game_number_display = QLabel(str(self.game_number))
        self.game_number_display.setStyleSheet("color: black; font-weight: bold;")
        self.game_number_display.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.game_number_display.setFont(QFont('Arial', 18))
        return self.game_number_display

    def update_game_number(self, game_number):
        self.game_number = game_number
        self.game_number_display.setText(str(self.game_number))

class Score(QWidget):
    def __init__(self, players, game_number, parent=None):
        super().__init__(parent)
        self.player1_data = players[0]
        self.player2_data = players[1]
        self.game_number = game_number
        self.init_ui()

    def init_ui(self):
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

    def update_scores(self, players_data):
        self.player1_score.update_score(players_data[0])
        self.player2_score.update_score(players_data[1])

    def update_game_number(self, game_number):
        self.game_number_module.update_game_number(game_number)
