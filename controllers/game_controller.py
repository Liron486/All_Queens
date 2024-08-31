from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtMultimedia import QSound
from utils import PlayerType, resize_and_show_normal, resource_path
from models.game_state import GameState
from logger import get_logger

WINNING_SOUND_PATH = resource_path('resources/sounds/winning.wav')
INVALID_MOVE_SOUND_PATH = resource_path('resources/sounds/invalid_move.wav')
MILLISECONDS_IN_SECOND = 1000

class GameController:
    """
    Controls the flow of the game, manages interactions between the model (game state)
    and the view, handles player moves, and manages the game's sound effects.
    """

    def __init__(self, game_state, view, is_edit_mode=False):
        """
        Initializes the GameController with the provided game state and view.

        Args:
            game_state (GameState): The current state of the game.
            view (QWidget): The view associated with the game.
            is_edit_mode (bool): Whether the game is in edit mode.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.game_state = game_state
        self.view = view
        self.signal_connected = False
        self._init_sounds()
        self._setup_connections()
        self.get_move_from_player()

    def get_move_from_player(self):
        """
        Initiates the process of getting a move from the current player,
        either human or AI.
        """
        player_type = self.game_state.get_current_player_type()
        if player_type is PlayerType.HUMAN:
            self.view.player_make_move_signal.connect(self._handle_move_from_player)
            self.signal_connected = True
        else:
            move = self.game_state.get_ai_move()
            self._execute_move(move, player_type)

    def start_new_game(self):
        """
        Starts a new game if the previous game has ended.
        Resets the game state and updates the view.
        """
        state = self.game_state
        if state.is_winner_found() and state.is_game_in_progress():
            self.logger.debug("Starting new game")
            route_to_reset = state.get_route_of_last_move().copy()
            state.start_new_game()
            self.view.start_new_game(state.get_board(), state.get_players(), route_to_reset, state.get_game_number())
            self.get_move_from_player()

    def pause_game(self):
        """
        Pauses the game. If the game is paused, disconnects player move signal.
        If the game is resumed, reconnects the signal if necessary.
        """
        is_paused = self.game_state.pause_game()
        if is_paused:
            self.view.game_paused()
            if self.signal_connected:
                self.view.player_make_move_signal.disconnect(self._handle_move_from_player)
                self.signal_connected = False
        else:
            self.view.game_resumed()
            if not self.game_state.is_winner_found():
                self.get_move_from_player()

    def undo_last_move(self):
        """
        Undoes the last move made in the game. Updates the game state and view accordingly.
        """
        state = self.game_state
        player_type = self.game_state.get_current_player_type()
        if state.is_winner_found():
            route_to_reset = state.get_route_of_last_move().copy()
            self.view.start_new_game(state.get_board(), state.get_players(), route_to_reset, state.get_game_number())
        elif self.signal_connected and not state.is_initial_setup():
            self.view.player_make_move_signal.disconnect(self._handle_move_from_player)
            self.signal_connected = False
        state.player_wants_to_undo_last_move()

    def show_full_screen(self):
        """
        Displays the view in full-screen mode.
        """
        self.view.showFullScreen()

    def exit_full_screen(self):
        """
        Exits full-screen mode and resizes the view to normal.
        """
        self.logger.debug("Exit full screen")
        resize_and_show_normal(self.view)

    def _init_sounds(self):
        """
        Initializes the sound effects for the game.
        Logs an error if there is an issue initializing the sounds.
        """
        try:
            self.winning_sound = QSound(WINNING_SOUND_PATH)
            self.invalid_move_sound = QSound(INVALID_MOVE_SOUND_PATH)
        except Exception as e:
            self.logger.error(f"Error initializing sounds: {e}")
            self.winning_sound = None
            self.invalid_move_sound = None

    def _setup_connections(self):
        """
        Sets up the connections between signals and slots for the view and game state.
        """
        self.view.exit_full_screen_signal.connect(self.exit_full_screen)
        self.view.key_pressed_signal.connect(self.start_new_game)
        self.view.b_key_was_pressed_signal.connect(self.undo_last_move)
        self.view.p_key_was_pressed_signal.connect(self.pause_game)
        self.game_state.invalid_move_signal.connect(lambda: self.invalid_move_sound.play())
        self.game_state.piece_was_chosen_signal.connect(self._piece_was_chosen_signal)
        self.game_state.player_finish_move_signal.connect(self._execute_move)

    def _piece_was_chosen_signal(self, pressed_cell, cells_to_reset, available_cells):
        """
        Handles the signal when a piece is chosen by the player.
        Updates the view to reflect the chosen piece and available moves.

        Args:
            pressed_cell (tuple): The cell where the piece was pressed.
            cells_to_reset (list): The cells that need to be reset.
            available_cells (list): The available cells for the chosen piece.
        """
        self.view.reset_cells_view(cells_to_reset)
        self.view.tag_cells_in_route(self.game_state.get_route_of_last_move())
        if pressed_cell:
            self.view.tag_available_cells(pressed_cell, available_cells)

    def _handle_move_from_player(self, row, col):
        """
        Handles the move made by the player when a cell is clicked.
        Checks the validity of the move.

        Args:
            row (int): The row of the cell that was clicked.
            col (int): The column of the cell that was clicked.
        """
        self.logger.debug(f"{self.game_state.get_current_player_name()} pressed on cell ({row},{col})")
        self.game_state.check_move(row, col)

    def _execute_move(self, move, player_type, is_undo_move=False):
        """
        Executes the move and schedules the continuation after a delay.

        Args:
            move (dict): The move to be executed.
            player_type (PlayerType): The type of player making the move.
            is_undo_move (bool): Whether the move is an undo operation.
        """
        self.logger.debug(f"{self.game_state.get_current_player_name()} makes the move from {move['from']} to {move['to']}")
        QApplication.processEvents()
        QTimer.singleShot(int(move['waiting_time'] * MILLISECONDS_IN_SECOND), lambda: self._continue_after_delay(move, player_type, is_undo_move))

    def _continue_after_delay(self, move, player_type, is_undo_move):
        """
        Continues the game after the scheduled delay, applying the move and checking for a winner.

        Args:
            move (dict): The move to be executed.
            player_type (PlayerType): The type of player making the move.
            is_undo_move (bool): Whether the move is an undo operation.
        """
        state = self.game_state
        if self._should_abort_move(player_type, is_undo_move):
            return

        self._apply_and_update_move(move, player_type, is_undo_move)

        if not state.is_game_in_progress():
            return

        if state.check_for_winner(move):
            self._handle_winner()
        else:
            self.get_move_from_player()

    def _should_abort_move(self, player_type, is_undo_move):
        """
        Determines whether the current move should be aborted.

        Args:
            player_type (PlayerType): The type of player making the move.
            is_undo_move (bool): Whether the move is an undo operation.

        Returns:
            bool: True if the move should be aborted, False otherwise.
        """
        state = self.game_state
        if state.is_need_to_abort_move() and not is_undo_move and player_type == PlayerType.AI:
            state.abort_move()
            return True
        return False

    def _handle_winner(self):
        """
        Handles the actions to be taken when a winner is found.
        Displays the winning message and plays the winning sound.
        """
        self.logger.debug(f"We Have a Winner!!! {self.game_state.get_next_player_name()} Wins!")
        self.view.display_winning_text(self.game_state.get_next_player_name())
        self.winning_sound.play()

    def _apply_and_update_move(self, move, player_type, is_undo_move):
        """
        Applies the move to the game state and updates the view.

        Args:
            move (dict): The move to be applied.
            player_type (PlayerType): The type of player making the move.
            is_undo_move (bool): Whether the move is an undo operation.
        """
        cells_to_reset = self.game_state.apply_move(move, is_undo_move)
        self.view.execute_move(move)
        self._finalize_move(move, cells_to_reset, player_type)

    def _finalize_move(self, move, cells_to_reset, player_type):
        """
        Finalizes the move by updating the view and disconnecting the player move signal if necessary.

        Args:
            move (dict): The move that was executed.
            cells_to_reset (list): The cells that need to be reset.
            player_type (PlayerType): The type of player making the move.
        """
        self.view.reset_cells_view(cells_to_reset)
        self.view.update_move_number(self.game_state.get_players())
        self.view.tag_cells_in_route(self.game_state.get_route_of_last_move())
        if player_type is PlayerType.HUMAN:
            self.view.player_make_move_signal.disconnect(self._handle_move_from_player)
            self.signal_connected = False
