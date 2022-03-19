from load_data import load_game_data


game = load_game_data()


class Game(object):
    def __init__(self, name, players, board):
        self.name = name
        self.players = players
        self.board = board