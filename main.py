import sys
from PyQt5.QtWidgets import QApplication
from controllers.welcome_controller import WelcomeController
from views.welcome_view import WelcomeWindow

def main():
    app = QApplication(sys.argv)
    view = WelcomeWindow()
    controller = WelcomeController(view)
    view.set_controller(controller)
    controller.show_welcome()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
