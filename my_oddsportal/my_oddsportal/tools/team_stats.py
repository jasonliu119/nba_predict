# -*- coding: utf-8 -*-

import pickle
from ..items import WinNbaGame
import json

f = open('./data/meta/win_game-2017-2018', 'r')
count = 0

class GameMeta:
    timestamp = 0
    game_id = 0
    is_home = False
    team = ''
    score = 0

    other_team = ''
    other_team_score = 0

    average_score = 100.0
    last_game_n_days_ago = 180.0
    prev_is_home = True

    def toJSON(self):
        return json.dumps(self, default = lambda o: o.__dict__, 
            sort_keys = True, indent = 4, ensure_ascii=False).encode('utf8')

team_dict = {} # team name : [GameMeta]

count_2017 = 0
count_2018 = 0

import time
def to_timestamp(time_str):
    return time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M"))

while True:
    try:
        game = pickle.load(f)
        count = count + 1

        time_str = game['time'].strip()
        if time_str.startswith('10') or time_str.startswith('11') or time_str.startswith('12'):
            time_str = '2017-' + time_str
            count_2017 = count_2017 + 1
        else:
            time_str = '2018-' + time_str
            count_2018 = count_2018 + 1

        timestamp = to_timestamp(time_str)
        game_id = int(game['game_id'])
        home_score = int(game['home_score'])
        away_score = int(game['away_score'])

        home_meta = GameMeta()
        home_meta.timestamp = timestamp
        home_meta.game_id = game_id
        home_meta.is_home = True
        home_meta.team = game['home']
        home_meta.score = home_score
        home_meta.other_team = game['away']
        home_meta.other_team_score = away_score

        away_meta = GameMeta()
        away_meta.timestamp = timestamp
        away_meta.game_id = game_id
        away_meta.is_home = False
        away_meta.team = game['away']
        away_meta.score = away_score
        away_meta.other_team = game['home']
        away_meta.other_team_score = home_score

        if game['home'] not in team_dict:
            team_dict[game['home']] = []
        if game['away'] not in team_dict:
            team_dict[game['away']] = []

        team_dict[game['home']].append(home_meta)
        team_dict[game['away']].append(away_meta)

    except EOFError:
        f.close()
        print(" --------- read " + str(count) + " games")
        print(" --------- count_2017 " + str(count_2017) + " games")
        print(" --------- count_2018 " + str(count_2018) + " games")
        print(" --------- count_teams " + str(len(team_dict)) + " teams")
        break

new_team_dict = {}
# post process
for team in team_dict:
    game_list = team_dict[team]
    game_list.sort(key = lambda x : x.timestamp)

    score_sum = 0
    for i in range(len(game_list)):
        game = game_list[i]
        score_sum = score_sum + game.score
        game_list[i].average_score = score_sum / 1.0 / (i + 1)
        if i == 0:
            continue
        game_list[i].last_game_n_days_ago = (game_list[i].timestamp - game_list[i - 1].timestamp) / 3600.0 / 24
        game_list[i].prev_is_home = game_list[i - 1].is_home
    new_team_dict[team] = game_list
    print "for team: " + team
    for game in game_list:
        print game.toJSON()

with open('./data/meta/post-processed-2017-2018.txt', 'wb') as f:
    pickle.dump(new_team_dict, f)
