from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QTimer
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
        self.signal_connected = False

    def setup_connections(self):
        self.view.exit_full_screen_signal.connect(self.exit_full_screen)
        self.view.key_pressed_signal.connect(self.start_new_game)
        self.view.b_key_was_pressed_signal.connect(self.undo_last_move)
        self.game_state.piece_was_chosen.connect(self.piece_was_chosen)
        self.game_state.player_finish_move.connect(self.execute_move)

    def undo_last_move(self):
        state = self.game_state
        player_type = self.game_state.get_currrent_player_type()
        if not state.is_game_in_progress():
            route_to_reset = state.get_route_of_last_move().copy()
            self.view.start_new_game(state.get_board(), state.get_players(), route_to_reset, state.get_game_number())
        elif self.signal_connected and not state.is_initial_setup():
            self.view.player_make_move_signal.disconnect(self.handle_move_from_player)
            self.signal_connected = False
        state.player_wants_to_undo_last_move()

    def get_move_from_player(self):
        player_type = self.game_state.get_currrent_player_type()
        if player_type is PlayerType.HUMAN:
            self.view.player_make_move_signal.connect(self.handle_move_from_player)
            self.signal_connected = True
        else:
            move = self.game_state.get_ai_move()
            self.execute_move(move, player_type)

    def piece_was_chosen(self, pressed_cell, cells_to_reset, available_cells):
        self.view.reset_cells_view(cells_to_reset)
        self.view.tag_cells_in_route(self.game_state.get_route_of_last_move())
        if pressed_cell:
            self.view.tag_available_cells(pressed_cell, available_cells)

    def execute_move(self, move, player_type, is_undo_move=False):
        self.logger.debug(f"{self.game_state.get_current_player_name()} makes the move from {move['from']} to {move['to']}")
        QApplication.processEvents()
        QTimer.singleShot(int(move['waiting_time'] * 1000), lambda: self.__continue_after_delay(move, player_type, is_undo_move))

    def __continue_after_delay(self, move, player_type, is_undo_move):
        state = self.game_state
        if state.is_need_to_abort_move() and not is_undo_move and player_type == PlayerType.AI:
            state.abort_move()
            return
        cells_to_reset = self.game_state.apply_move(move, is_undo_move)
        self.view.execute_move(move)
        self.__end_move_actions(move, cells_to_reset, player_type, is_undo_move)

        if self.game_state.check_for_winner(move):
            self.logger.debug(f"We Have a Winner!!! {self.game_state.get_next_player_name()} Wins!")
            self.view.display_winning_text(self.game_state.get_next_player_name())
        else:
            self.get_move_from_player() 

    def handle_move_from_player(self, row, col):
        self.logger.debug(f"{self.game_state.get_current_player_name()} pressed on cell ({row},{col})")
        self.game_state.check_move(row,col)

    def start_new_game(self):
        state = self.game_state
        if not state.is_game_in_progress():
            self.logger.debug("Starting new game")
            route_to_reset = state.get_route_of_last_move().copy()
            state.start_new_game()
            self.view.start_new_game(state.get_board(), state.get_players(), route_to_reset, state.get_game_number())
            self.get_move_from_player()

    def show_full_screen(self):
        self.view.show()
        self.view.showFullScreen()

    def exit_full_screen(self):
        self.logger.debug("Exit full screen")
        resize_and_show_normal(self.view)

    def __end_move_actions(self, move, cells_to_reset, player_type, is_undo_move):
        self.view.reset_cells_view(cells_to_reset)
        self.view.update_move_number(self.game_state.get_players())
        self.view.tag_cells_in_route(self.game_state.get_route_of_last_move())
        if player_type == PlayerType.HUMAN:
            self.view.player_make_move_signal.disconnect(self.handle_move_from_player)
            self.signal_connected = False