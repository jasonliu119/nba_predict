import pickle
from ..items import WinNbaGame
import time
import csv

class Team:
    def __init__(self, name):
        self.name = name # str name
        self.num_home_game = 0
        self.num_away_game = 0
        self.num_home_game_win = 0
        self.num_away_game_win = 0
        self.sum_score_got_home = 0 # sum of the score that this team got in all the home games
        self.sum_score_lost_home = 0 # sum of the score that this team lost (the other team got) in all the home games
        self.sum_score_got_away = 0
        self.sum_score_lost_away = 0
        self.last_game_timestamp = 0 # timestamp of the last game
        self.win_lose_history = [] # int array: 1 means win, 0 means lose

'''
game class:
class WinNbaGame(scrapy.Item):
    game_id = scrapy.Field()
    home = scrapy.Field()
    away = scrapy.Field()
    home_score = scrapy.Field()
    away_score = scrapy.Field()
    time = scrapy.Field()
    game_type = scrapy.Field()
'''
def to_timestamp(time_str):
    if time_str.startswith('1'): # e.g., 10-27 00:00
        time_str = '2017-' + time_str
    else:
        time_str = '2018-' + time_str
    return time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M"))



def read_game_meta_file_and_output_features(meta_file_path, feature_csv_path):
    # Step 1: read all the games info
    team_data_dict = {} # from team string name to Team object, used as the stats
    game_data_dict = {} # from int timestamp to game

    f = open(meta_file_path, 'r')
    while True:
        try:
            game = pickle.load(f)
            game_data_dict[int(game['game_id'])] = game

            home_team = game['home']
            away_team = game['away']
            if home_team not in team_data_dict:
                team_data_dict[home_team] = Team(home_team)
            if away_team not in team_data_dict:
                team_data_dict[away_team] = Team(away_team)
        except EOFError:
            f.close()
            print(" --------- totally read: " + str(len(game_data_dict)) + " games") # 1127 games
            print(" --------- totally read: " + str(len(team_data_dict)) + " teams") # 30 teams
            break

    # Step 2: construct the stats and output features (first 127 games will not be outputed)
    id_set = game_data_dict.keys()
    id_set.sort() # the earlier game, the smaller id
    count = 0

    csvfile = open('names.csv', 'wb')
    fieldnames = ['first_name', 'last_name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    '''
    features per game:
    1. home team per game got score
    2. home team per game lost score
    3. home team per home game got score
    4. home team per home game lost score
    5. home team last win number of the last 10 game
    6. home team rest time (in days)
    7. home team ranking of all the teams
    8. home team home win rate
    9. home team win rate

    1. away team per game got score
    2. away team per game lost score
    3. away team per away game got score
    4. away team per away game lost score
    5. away team last win number of the last 10 game
    6. away team rest time (in days)
    7. away team ranking of all the teams
    8. away team away win rate
    9. away team win rate

    label:
    home win --> 1
    away win --> 0

    binary classification
    '''

    writer.writeheader(
        'home team per game got score',
        'home team per game lost score',
        'home team per home game got score',
        'home team per home game lost score',
        'home team last win number of the last 10 game',
        'home team rest time (in days)',
        'home team ranking of all the teams',
        'home team home win rate',
        'home team win rate',
        'away team per game got score',
        'away team per game lost score',
        'away team per away game got score',
        'away team per away game lost score',
        'away team last win number of the last 10 game',
        'away team rest time (in days)',
        'away team ranking of all the teams',
        'away team away win rate',
        'away team win rate')

    for id in id_set:
        game = game_data_dict[id]
        home = game['home']
        away = game['away']
        home_score = int(game['home_score'])
        away_score = int(game['away_score'])
        is_home_win = home_score > away_score
        last_game_timestamp = to_timestamp(game['time'])

        count += 1
        if count >= 127: # need to boostrap; don't add the first games into features
            writer.writerow({
            'home team per game got score':,
            'home team per game lost score':,
            'home team per home game got score':,
            'home team per home game lost score':,
            'home team last win number of the last 10 game':,
            'home team rest time (in days)':,
            'home team ranking of all the teams':,
            'home team home win rate':,
            'home team win rate':,
            'away team per game got score':,
            'away team per game lost score':,
            'away team per away game got score':,
            'away team per away game lost score':,
            'away team last win number of the last 10 game':,
            'away team rest time (in days)':,
            'away team ranking of all the teams':,
            'away team away win rate':,
            'away team win rate':})
            

        # for home
        team_data_dict[home].num_home_game += 1
        team_data_dict[home].sum_score_got_home += home_score
        team_data_dict[home].sum_score_lost_home += away_score
        team_data_dict[home].last_game_timestamp = last_game_timestamp
        if is_home_win:
            team_data_dict[home].num_home_game_win += 1
            team_data_dict[home].win_lose_history.append(1)
        else:
            team_data_dict[home].win_lose_history.append(0)
        

        # for away
        team_data_dict[away].num_away_game += 1
        team_data_dict[away].sum_score_got_away += away_score
        team_data_dict[away].sum_score_lost_away += home_score
        team_data_dict[away].last_game_timestamp = last_game_timestamp
        if not is_home_win:
            team_data_dict[away].num_away_game_win += 1
            team_data_dict[away].win_lose_history.append(1)
        else:
            team_data_dict[away].win_lose_history.append(0)

if __name__=="__main__":
    meta_file_path = './data/meta/win_game-2017-2018'
    feature_csv_path = ""
    read_game_meta_file_and_output_features(meta_file_path, feature_csv_path)
