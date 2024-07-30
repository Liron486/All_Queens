import sys
from logger import setup_logger
from game_manager import GameManager

def main():
    setup_logger()
    all_queens = GameManager()
    all_queens.load_game()    
    sys.exit()

if __name__ == '__main__':
    main()
