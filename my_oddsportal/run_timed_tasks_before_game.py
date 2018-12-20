# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import time
import datetime
import calendar
import pickle
import os
from my_oddsportal.items import WinNbaGame
from sets import Set

YEAR = str(datetime.datetime.now().year)

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

def get_team_id(chinese):
    '''
    01 Celtics
    02 Nets
    03 Knicks
    04 76ers
    05 Raptors
    06 Warriors
    07 Clippers
    08 Lakers
    09 Suns
    10 Kings
    11 Bulls
    12 Cavaliers
    13 Pistons
    14 Pacers
    15 Bucks
    16 Hawks
    17 Hornets
    18 Heat
    19 Magic
    20 Wizards
    21 Nuggets
    22 Timberwolves
    23 Thunder
    24 Trail Blazers
    25 Jazz
    26 Mavericks
    27 Rockets
    28 Grizzlies
    29 Pelicans
    30 Spurs
    '''
    if "凯尔特" in chinese:
        return "01"
    if '篮网' in chinese:
        return "02"
    if '尼克斯' in chinese:
        return "03"
    if '76人' in chinese:
        return "04"
    if '猛龙' in chinese:
        return "05"

    if '勇士' in chinese:
        return "06"
    if '快船' in chinese:
        return "07"
    if '湖人' in chinese:
        return "08"
    if '太阳' in chinese:
        return "09"
    if '国王' in chinese:
        return "10"

    if '公牛' in chinese:
        return "11"
    if '骑士' in chinese:
        return "12"
    if '活塞' in chinese:
        return "13"
    if '步行者' in chinese:
        return "14"
    if '雄鹿' in chinese:
        return "15"

    if '老鹰' in chinese:
        return "16"
    if '黄蜂' in chinese:
        return "17"
    if '热火' in chinese:
        return "18"
    if '魔术' in chinese:
        return "19"
    if '奇才' in chinese:
        return "20"

    if '掘金' in chinese:
        return "21"
    if '森林狼' in chinese:
        return "22"
    if '雷霆' in chinese:
        return "23"
    if '开拓者' in chinese:
        return "24"
    if '爵士' in chinese:
        return "25"

    if '独行侠' in chinese:
        return "26"
    if '火箭' in chinese:
        return "27"
    if '灰熊' in chinese:
        return "28"
    if '鹈鹕' in chinese:
        return "29"
    if '马刺' in chinese:
        return "30"

def find_game_today_and_output():
    from datetime import datetime
    from pytz import timezone
    import pytz
    pst = pytz.timezone('America/Los_Angeles')
    file = open("./today.txt", "wb")

    now = int(time.time())
    game_meta = read_game_meta()
    now = datetime.now()
    now = pst.localize(now)
    for game in game_meta:
        ts = strptime(game['time']) - 8 * 3600
        datetime_obj = datetime.fromtimestamp(ts)
        datetime_obj = pst.localize(datetime_obj)
        if now.strftime("%Y-%m-%d") == datetime_obj.strftime("%Y-%m-%d"):
            print game_str(game)
            '''
            live
            09
            10
            1545264000
            '''
            file.write('live\n')
            file.write(get_team_id(game['away']))
            file.write('\n')
            file.write(get_team_id(game['home']))
            file.write('\n')
            file.write(str(strptime(game['time'])) + '\n')
            file.write('\n')

    os.system("mkdir ~/nba/")
    os.system("mv ./today.txt ~/nba/")

def run_forever():
    time_granularity = 600
    check_time_granularity = 300
    while True:
        find_game_today_and_output()

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
            os.system("sh run_decreasing_rule_with_seeds.sh {}".format(game_str))

        time.sleep(check_time_granularity)

if __name__ == '__main__':
    run_forever()
