import pickle
from ..items import WinNbaGame

f = open('./data/win_game-2017-2018', 'r')
count = 0

while True:
    try:
        count = count + 1
        game = pickle.load(f)
        print(" ************* type " + game['game_type'] + ", time " + game['time'] + ", id " + game['game_id'] + ", home " + 
            game['home'] + ", away " + game['away'] + ", home_score " + game['home_score'] + ", away_score " + game['away_score'])
    except EOFError:
        f.close()
        print(" --------- read " + str(count) + " games")
        break
