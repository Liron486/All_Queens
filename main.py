import sys
from game_manager import GameManager

def main():
    all_queens = GameManager()
    all_queens.start_game()    
    sys.exit()

if __name__ == '__main__':
    main()
