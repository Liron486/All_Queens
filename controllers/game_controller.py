from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtMultimedia import QSound
from utils import PlayerType, resize_and_show_normal, resource_path
from models.game_state import GameState
from logger import get_logger

WINNING_SOUND_PATH = resource_path('resources/sounds/winning.wav')
LOSING_SOUND_PATH = resource_path('resources/sounds/losing.wav')
INVALID_MOVE_SOUND_PATH = resource_path('resources/sounds/invalid_move.wav')
MILLISECONDS_IN_SECOND = 1000

class GameController(QObject):
    """
    Controls the flow of the game, manages interactions between the model (game state)
    and the view, handles player moves, and manages the game's sound effects.
    """

    back_to_settings_singal = pyqtSignal()

    def __init__(self, game_state, view):
        """
        Initializes the GameController with the provided game state and view.

        Args:
            game_state (GameState): The current state of the game.
            view (QWidget): The view associated with the game.
            is_edit_mode (bool): Whether the game is in edit mode.
        """
        super().__init__()
        self._logger = get_logger(self.__class__.__name__)
        self._game_state = game_state
        self._view = view
        self._signal_connected = False
        self._abort_game = False
        self._init_sounds()
        self._setup_connections()
        if self._game_state.is_edit_mode:
            self._init_edit_mode()
        else:
            self._get_move_from_player()

    def start_new_game(self):
        """
        Starts a new game if the previous game has ended.
        Resets the game state and updates the view.
        """
        state = self._game_state
        if state.is_winner_found and state.is_game_in_progress:
            self._logger.debug("Starting new game")
            route_to_reset = state.route_of_last_move.copy()
            state.start_new_game()
            self._view.start_new_game(state.board, state.players, route_to_reset, state.game_number)
            self._get_move_from_player()

    def back_to_settings(self):
        self._abort_game = True
        self.back_to_settings_singal.emit()
        
    def pause_game(self):
        """
        Pauses the game. If the game is paused, disconnects player move signal.
        If the game is resumed, reconnects the signal if necessary.
        """
        is_paused = self._game_state.pause_game()
        if is_paused:
            self._view.game_paused()
            if self._signal_connected:
                self._view.player_click_signal.disconnect(self._handle_move_from_player)
                self._signal_connected = False
        else:
            self._view.game_resumed()
            if not self._game_state.is_winner_found:
                self._get_move_from_player()

    def undo_last_move(self):
        """
        Undoes the last move made in the game. Updates the game state and view accordingly.
        """
        state = self._game_state
        player_type = self._game_state.current_player_type
        if state.is_winner_found:
            route_to_reset = state.route_of_last_move.copy()
            self._view.start_new_game(state.board, state.players, route_to_reset, state.game_number)
        elif self._signal_connected and not state.is_initial_setup():
            self._view.player_click_signal.disconnect(self._handle_move_from_player)
            self._signal_connected = False
        state.player_wants_to_undo_last_move()

    def hide_screen(self):
        """
        Hides the game view.
        """
        self._view.hide()

    def show_full_screen(self):
        """
        Displays the view in full-screen mode.
        """
        self._view.showFullScreen()

    def exit_full_screen(self):
        """
        Exits full-screen mode and resizes the view to normal.
        """
        self._logger.debug("Exit full screen")
        resize_and_show_normal(self._view)

    def _init_sounds(self):
        """
        Initializes the sound effects for the game.
        Logs an error if there is an issue initializing the sounds.
        """
        try:
            self._winning_sound = QSound(WINNING_SOUND_PATH)
            self._losing_sound = QSound(LOSING_SOUND_PATH)
            self._invalid_move_sound = QSound(INVALID_MOVE_SOUND_PATH)
        except Exception as e:
            self._logger.error(f"Error initializing sounds: {e}")
            self._winning_sound = None
            self._losing_sound = None
            self._invalid_move_sound = None

    def piece_was_chosen(self, pressed_cell, cells_to_reset, available_cells):
        """
        Handles the signal when a piece is chosen by the player.
        Updates the view to reflect the chosen piece and available moves.

        Args:
            pressed_cell (tuple): The cell where the piece was pressed.
            cells_to_reset (list): The cells that need to be reset.
            available_cells (list): The available cells for the chosen piece.
        """
        self._view.reset_cells_view(cells_to_reset)
        self._view.tag_cells_in_route(self._game_state.route_of_last_move)
        if pressed_cell:
            self._view.tag_available_cells(pressed_cell, available_cells)

    def execute_move(self, move, player_type, is_undo_move=False):
        """
        Executes the move and schedules the continuation after a delay.

        Args:
            move (dict): The move to be executed.
            player_type (PlayerType): The type of player making the move.
            is_undo_move (bool): Whether the move is an undo operation.
        """
        self._logger.debug(f"{self._game_state.current_player_name} makes the move from {move['from']} to {move['to']}")
        QApplication.processEvents()
        QTimer.singleShot(int(move['waiting_time'] * MILLISECONDS_IN_SECOND), lambda: self._continue_after_delay(move, player_type, is_undo_move))
        
    def _setup_connections(self):
        """
        Sets up the connections between signals and slots for the view and game state.
        """
        self._view.exit_full_screen_signal.connect(self.exit_full_screen)
        self._view.key_pressed_signal.connect(self.start_new_game)
        self._view.b_key_was_pressed_signal.connect(self.undo_last_move)
        self._view.p_key_was_pressed_signal.connect(self.pause_game)
        self._view.back_was_pressed_signal.connect(self.back_to_settings)
        self._game_state.invalid_move_signal.connect(lambda: self._invalid_move_sound.play())
        self._game_state.piece_was_chosen_signal.connect(self.piece_was_chosen)
        self._game_state.player_finish_move_signal.connect(self.execute_move)

    def _init_edit_mode(self):
        self._view.enter_was_pressed_signal.connect(self._exit_edit_mode)
        self._view.player_hold_cell_signal.connect(self._handle_holding_cell)
        self._view.player_release_signal.connect(self._handle_release_on_cell)

    def _exit_edit_mode(self):
        self._game_state.exit_edit_mode()
        self._view.enter_was_pressed_signal.disconnect(self._exit_edit_mode)
        self._view.player_hold_cell_signal.disconnect(self._handle_holding_cell)
        self._view.player_release_signal.disconnect(self._handle_release_on_cell)
        self._move_finished()

    def _get_move_from_player(self):
        """
        Initiates the process of getting a move from the current player,
        either human or AI.
        """
        player_type = self._game_state.current_player_type
        if player_type is PlayerType.HUMAN:
            self._view.player_click_signal.connect(self._handle_move_from_player)
            self._signal_connected = True
        else:
            move = self._game_state.get_ai_move()
            self.execute_move(move, player_type)

    def _handle_release_on_cell(self, row, col):
        state = self._game_state
        piece = state.piece_type_edit_mode
        valid_edit_move, pressed_cell = state.edit_board_to(row, col)
        if valid_edit_move:
            self._view._set_cell((row,col), piece)
        elif pressed_cell:
            self._view._set_cell(pressed_cell, piece)
        
    def _handle_holding_cell(self, row, col):
        state = self._game_state
        is_valid_cell = state.edit_board_from(row, col)

        if is_valid_cell:
            cell = (row, col)
            state.piece_type_edit_mode = self._view.get_cell_piece_type(cell)
            state.pressed_cell_edit_mode = cell
            self._view.pick_piece(cell)

    def _handle_move_from_player(self, row, col):
        """
        Handles the move made by the player when a cell is clicked.
        Checks the validity of the move.

        Args:
            row (int): The row of the cell that was clicked.
            col (int): The column of the cell that was clicked.
        """
        state = self._game_state
        self._logger.debug(f"{state.current_player_name} pressed on cell ({row},{col})")
        state.check_move_validity(row, col)

    def _continue_after_delay(self, move, player_type, is_undo_move):
        """
        Continues the game after the scheduled delay, applying the move and checking for a winner.

        Args:
            move (dict): The move to be executed.
            player_type (PlayerType): The type of player making the move.
            is_undo_move (bool): Whether the move is an undo operation.
        """
        state = self._game_state
        if self._should_abort_move(player_type, is_undo_move):
            return

        self._apply_and_update_move(move, player_type, is_undo_move)

        if not state.is_game_in_progress:
            return

        self._move_finished(move)

    def _move_finished(self, move=None):
        if not self._abort_game:
            if self._game_state.check_for_winner(move):
                self._handle_winner()
            else:
                self._get_move_from_player()

    def _should_abort_move(self, player_type, is_undo_move):
        """
        Determines whether the current move should be aborted.

        Args:
            player_type (PlayerType): The type of player making the move.
            is_undo_move (bool): Whether the move is an undo operation.

        Returns:
            bool: True if the move should be aborted, False otherwise.
        """
        state = self._game_state
        if state.is_need_to_abort_move() and not is_undo_move and player_type == PlayerType.AI:
            state.abort_move()
            return True
        return False

    def _handle_winner(self):
        """
        Handles the actions to be taken when a winner is found.
        Displays the winning message and plays the winning sound.
        """
        self._logger.debug(f"We Have a Winner!!! {self._game_state.next_player_name} Wins!")
        self._view.display_winning_text(self._game_state.next_player_name)
        self._play_end_game_sound()

    def _play_end_game_sound(self):
        """
        Plays the appropriate end game sound based on the game outcome and player type.

        This method checks if the game is a human versus computer match and if the 
        current player is AI. If the AI is the current player, the losing sound will 
        be played, indicating that the human player lost. Otherwise, the winning 
        sound will be played.
        """
        state = self._game_state
        if state.is_human_vs_computer() and state.next_player_type is PlayerType.AI:
            self._losing_sound.play()
        else:
            self._winning_sound.play()

    def _apply_and_update_move(self, move, player_type, is_undo_move):
        """
        Applies the move to the game state and updates the view.

        Args:
            move (dict): The move to be applied.
            player_type (PlayerType): The type of player making the move.
            is_undo_move (bool): Whether the move is an undo operation.
        """
        cells_to_reset = self._game_state.apply_move(move, is_undo_move)
        self._view.execute_move(move)
        self._finalize_move(move, cells_to_reset, player_type)

    def _finalize_move(self, move, cells_to_reset, player_type):
        """
        Finalizes the move by updating the view and disconnecting the player move signal if necessary.

        Args:
            move (dict): The move that was executed.
            cells_to_reset (list): The cells that need to be reset.
            player_type (PlayerType): The type of player making the move.
        """
        self._view.reset_cells_view(cells_to_reset)
        self._view.update_move_number(self._game_state.players)
        self._view.tag_cells_in_route(self._game_state.route_of_last_move)
        if player_type is PlayerType.HUMAN:
            self._view.player_click_signal.disconnect(self._handle_move_from_player)
            self._signal_connected = False
