import pickle
from ..items import WinNbaGame

f = open('./data/win_game-2017-2018', 'r')

while True:
    try:
        game = pickle.load(f)
        print(" ************* " + game['game_type'])
    except EOFError:
        f.close()
        print(" --------- read finished ")
        break
