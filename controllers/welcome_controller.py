from PyQt5.QtCore import QObject, pyqtSignal
from utils import resize_and_show_normal
from logger import get_logger

class WelcomeController(QObject):
    """
    Controls the welcome view, handling user interactions such as switching to the settings view
    and managing the display mode of the view.
    """
    
    request_settings_view_signal = pyqtSignal()

    def __init__(self, view):
        """
        Initializes the WelcomeController with the provided view.

        Args:
            view (QWidget): The view associated with the welcome screen.
        """
        super().__init__()
        self._logger = get_logger(self.__class__.__name__)
        self._view = view
        self._setup_connections()

    def show_full_screen(self):
        """
        Displays the welcome view in full-screen mode.
        """
        self._view.show()
        self._view.showFullScreen()

    def hide_screen(self):
        """
        Hides the welcome view.
        """
        self._view.hide()

    def exit_full_screen(self):
        """
        Exits full-screen mode and resizes the view to its normal size.
        """
        self._logger.debug("Exit full screen")
        resize_and_show_normal(self._view)

    def handle_switch_to_settings(self):
        """
        Emits a signal to request switching to the settings view when the relevant
        user action is triggered.
        """
        self.request_settings_view_signal.emit()

    def _setup_connections(self):
        """
        Sets up the signal-slot connections between the view and the controller.
        """
        self._view.exit_full_screen_signal.connect(self.exit_full_screen)
        self._view.switch_to_settings_signal.connect(self.handle_switch_to_settings)
