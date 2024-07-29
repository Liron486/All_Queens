import time
from PyQt5.QtCore import pyqtSignal
from utils import PlayerType, resize_and_show_normal
from models.game_state import GameState
from logger import get_logger

class GameController:
    def __init__(self, game_state, view, is_edit_mode=False):
        self.logger = get_logger(self.__class__.__name__)
        self.game_state = game_state
        self.view = view 
        self.setup_connections()
        self.get_move_from_player()

    def setup_connections(self):
        self.view.exit_full_screen_signal.connect(self.exit_full_screen)
        self.game_state.piece_was_chosen.connect(self.piece_was_chosen)
        self.game_state.player_made_move.connect(self.execute_move)

    def get_move_from_player(self):
        player_type = self.game_state.get_currrent_player_type()        
        if player_type is PlayerType.HUMAN:
            self.view.player_make_move_signal.connect(self.handle_move_from_player)
        else:
            move = self.game_state.get_ai_move()
            self.move_finished([], move)

    def piece_was_chosen(self, pressed_cell, cells_to_reset, available_cells):
        self.view.reset_cells_view(cells_to_reset)
        if pressed_cell:
            self.view.tag_available_cells(pressed_cell, available_cells)

    def execute_move(self, move, cells_to_reset):
        self.logger.debug(f"player make the move {move['from']},{move['to']}")
        time.sleep(move['waiting_time'])
        self.view.execute_move(move)
        self.__end_move_actions(cells_to_reset)

        if self.game_state.check_for_winner(move):
            self.logger.debug(f"We Have a Winner!!! {self.game_state.get_current_player_name()} Wins!")
        else:
            self.get_move_from_player()

    def handle_move_from_player(self, row, col):
        self.logger.debug(f"player pressed on cell ({row},{col})")
        self.game_state.check_move(row,col)

    def show_full_screen(self):
        self.view.show()
        self.view.showFullScreen()

    def exit_full_screen(self):
        self.logger.debug("Exit full screen")
        resize_and_show_normal(self.view)

    def __end_move_actions(self, cells_to_reset):
        self.view.reset_cells_view(cells_to_reset)
        self.view.player_make_move_signal.disconnect(self.handle_move_from_player)