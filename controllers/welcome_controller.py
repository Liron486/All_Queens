class WelcomeController:
    def __init__(self, view):
        self.view = view
        self.view.escapePressed.connect(self.exit_full_screen)

    def show_welcome(self):
        self.view.show()

    def play(self):
        print("Transition to settings page")  # Placeholder for transitioning to the settings page

    def exit_full_screen(self):
        self.view.showNormal()  # Exits full screen mode
