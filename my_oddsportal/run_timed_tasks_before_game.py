import time
import datetime
import calendar
import pickle
from my_oddsportal.items import WinNbaGame
from sets import Set

YEAR = '2018'

def strptime(string):
    # sample: 10-30 00:30
    # return time.mktime()
    t = datetime.datetime.strptime(YEAR + " " + string, "%Y %m-%d %H:%M").timetuple()
    return calendar.timegm(t)

def test_strptime():
    s = ["01-01 00:01", "12-21 20:19"]
    for t in s:
        print strptime(t)

def game_str(game):
    game_id = "0"
    if 'game_id' in game:
        game_id = game['game_id']

    return " ************* type " + game['game_type'] + ", time " + str(strptime(game['time'])) + ", id " + game_id + ", home " + \
        game['home'] + ", away " + game['away'] + ", home_score " + game['home_score'] + ", away_score " + game['away_score']

def read_game_meta(path = ''):
    game_meta = []
    if path == '':
        path = './data/collected-meta/win_game-2018-2019'
    f = open(path, 'r')

    count = 0
    while True:
        try:
            count = count + 1
            game = pickle.load(f)
            # print(game_str(game))
            game_meta.append(game)
        except EOFError:
            f.close()
            print(" --------- read " + str(count) + " games")
            break

    return game_meta

def is_previous_save_start_soon(id):
    previous_set = Set()
    with open('./data/log/processed_ids.txt', 'r') as f:
        line = f.readline()
        while line:
            previous_set.add(line.strip())
            line = f.readline()

    if id in previous_set:
        return True

    with open('./data/log/processed_ids.txt', 'a+') as f:
        f.write(id + '\n')

    return False


def find_game_start_soon(game_meta, time_granularity):
    game_id_start_soon = []
    now = int(time.time())
    for game in game_meta:
        if abs(now - strptime(game['time'])) <= time_granularity:
            if 'game_id' not in game or game['game_id'] == '0':
                print "WARNING: game_id_start_soon got 0 id: " + game_str(game)
                continue
            game_id_start_soon.append(game['game_id'])

    return game_id_start_soon

if __name__ == '__main__':
    time_granularity = 600
    check_time_granularity = 300
    while True:
        # get the game meta of 2018-2019 season
        game_meta = read_game_meta()

        # get the games that will start in 10 minuts
        game_start_soon = find_game_start_soon(game_meta, time_granularity)

        game_str = ''

        for game in game_start_soon:
            if is_previous_save_start_soon(str(game)):
                continue

            game_str += str(game)
            game_str += ' '
        game_str = '\"' + game_str.strip() + '\"'
        print "--- start-soon games: " + game_str

        if (game_str != "\"\"" and len(game_start_soon) > 0):
            # run the script to analyse the games starting soon
            import os
            os.system("sh run_decreasing_rule_with_seeds.sh {}".format(game_str))

        time.sleep(check_time_granularity)

