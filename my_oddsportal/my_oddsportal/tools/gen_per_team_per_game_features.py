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

    def per_game_got_score(self):
        return (self.sum_score_got_home + self.sum_score_got_away) * 1.0 / (self.num_home_game + self.num_away_game)

    def per_home_game_got_score(self):
        return self.sum_score_got_home * 1.0 / self.num_home_game

    def per_away_game_got_score(self):
        return self.sum_score_got_away * 1.0 / self.num_away_game

    def per_game_lost_score(self):
        return (self.sum_score_lost_home + self.sum_score_lost_away) * 1.0 / (self.num_home_game + self.num_away_game)

    def per_home_game_lost_score(self):
        return self.sum_score_lost_home * 1.0 / self.num_home_game

    def per_away_game_lost_score(self):
        return self.sum_score_lost_away * 1.0 / self.num_away_game

    def last_win_number_of_the_last_10_game(self):
        max_index = len(self.win_lose_history) - 1
        k = 0
        win_count = 0
        while (max_index - k >= 0) and k < 10:
            if self.win_lose_history[max_index - k] == 1:
                win_count += 1
            k += 1
        return win_count

    def win_rate(self):
        return (self.num_home_game_win + self.num_away_game_win) * 1.0 / (self.num_home_game + self.num_away_game)

    def home_win_rate(self):
        return self.num_home_game_win * 1.0 / self.num_home_game

    def away_win_rate(self):
        return self.num_away_game_win * 1.0 / self.num_away_game    

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

def rest_time_in_days(now, ts):
    return (now - ts) * 1.0 / 3600 / 24

def get_rank_in_all_teams(team_data_dict, team_name):
    teams = []
    for k in team_data_dict:
        teams.append(team_data_dict[k])
    teams.sort(key = lambda x : x.win_rate(), reverse = True)
    rank = 0

    for team in teams:
        rank += 1
        if team.name == team_name:
            return rank

    return 31

def how_long_after_season_begin(timestamp):
    delta = timestamp - to_timestamp("10-01 00:00")
    max_delta = to_timestamp("05-01 00:00") - to_timestamp("10-01 00:00")
    return delta / 1.0 / max_delta

def read_game_meta_file_and_output_features(meta_file_path, feature_csv_path):
    # Step 1: read all the games info
    team_data_dict = {} # from team string name to Team object, used as the stats
    game_data_dict = {} # from int timestamp to game

    f = open(meta_file_path, 'r')
    use_win_rate_predict_correct_count = 0
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

    '''
    label:
    home win --> 1
    away win --> 0

    binary classification
    '''

    csvfile = open(feature_csv_path, 'wb')
    fieldnames = [
        'home_team_per_game_got_score',
        'home_team_per_game_lost_score',
        'home_team_per_home_game_got_score',
        'home_team_per_home_game_lost_score',
        'home_team_last_win_number_of_the_last_10_game',
        'home_team_rest_time_in_days',
        'home_team_ranking_of_all_the_teams',
        'home_team_home_win_rate',
        'home_team_win_rate',
        'away_team_per_game_got_score',
        'away_team_per_game_lost_score',
        'away_team_per_away_game_got_score',
        'away_team_per_away_game_lost_score',
        'away_team_last_win_number_of_the_last_10_game',
        'away_team_rest_time_in_days',
        'away_team_ranking_of_all_the_teams',
        'away_team_away_win_rate',
        'away_team_win_rate',
        'how_long_after_season_begin',
        'home_win_or_lose']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for id in id_set:
        game = game_data_dict[id]
        home = game['home']
        away = game['away']
        home_score = int(game['home_score'])
        away_score = int(game['away_score'])
        is_home_win = home_score > away_score
        last_game_timestamp = to_timestamp(game['time'])

        def norm_score(score):
            return score / 100.0

        def norm_rest_days(rest_time_in_days):
            if rest_time_in_days < 0:
                rest_time_in_days = 0.3
            return min(rest_time_in_days / 7.0, 1.0)

        count += 1
        if count >= 127: # need to boostrap; don't add the first games into features
            home_team_per_game_got_score = norm_score(team_data_dict[home].per_game_got_score())
            home_team_per_game_lost_score = norm_score(team_data_dict[home].per_game_lost_score())
            home_team_per_home_game_got_score = norm_score(team_data_dict[home].per_home_game_got_score())
            home_team_per_home_game_lost_score = norm_score(team_data_dict[home].per_home_game_lost_score())
            home_team_last_win_number_of_the_last_10_game = team_data_dict[home].last_win_number_of_the_last_10_game() / 10.0
            home_team_rest_time = norm_rest_days(rest_time_in_days(last_game_timestamp, team_data_dict[home].last_game_timestamp))
            home_team_ranking_of_all_the_teams = get_rank_in_all_teams(team_data_dict, home)
            home_team_home_win_rate = team_data_dict[home].home_win_rate()
            home_team_win_rate = team_data_dict[home].win_rate()

            away_team_per_game_got_score = norm_score(team_data_dict[away].per_game_got_score())
            away_team_per_game_lost_score = norm_score(team_data_dict[away].per_game_lost_score())
            away_team_per_away_game_got_score = norm_score(team_data_dict[away].per_away_game_got_score())
            away_team_per_away_game_lost_score = norm_score(team_data_dict[away].per_away_game_lost_score())
            away_team_last_win_number_of_the_last_10_game = team_data_dict[away].last_win_number_of_the_last_10_game() / 10.0
            away_team_rest_time = norm_rest_days(rest_time_in_days(last_game_timestamp, team_data_dict[away].last_game_timestamp))
            away_team_ranking_of_all_the_teams = get_rank_in_all_teams(team_data_dict, away)
            away_team_away_win_rate = team_data_dict[away].away_win_rate()
            away_team_win_rate = team_data_dict[away].win_rate()

            how_long_after_season_begin_value = how_long_after_season_begin(last_game_timestamp);

            home_win_or_lose = 1
            if home_score < away_score:
                home_win_or_lose = 0

            if (home_score < away_score and home_team_win_rate < away_team_win_rate) or (home_score > away_score and home_team_win_rate > away_team_win_rate):
                use_win_rate_predict_correct_count += 1

            writer.writerow({
            'home_team_per_game_got_score': home_team_per_game_got_score,
            'home_team_per_game_lost_score': home_team_per_game_lost_score,
            'home_team_per_home_game_got_score': home_team_per_home_game_got_score,
            'home_team_per_home_game_lost_score': home_team_per_home_game_lost_score,
            'home_team_last_win_number_of_the_last_10_game': home_team_last_win_number_of_the_last_10_game,
            'home_team_rest_time_in_days': home_team_rest_time,
            'home_team_ranking_of_all_the_teams': home_team_ranking_of_all_the_teams,
            'home_team_home_win_rate': home_team_home_win_rate,
            'home_team_win_rate': home_team_win_rate,
            'away_team_per_game_got_score': away_team_per_game_got_score,
            'away_team_per_game_lost_score': away_team_per_game_lost_score,
            'away_team_per_away_game_got_score': away_team_per_away_game_got_score,
            'away_team_per_away_game_lost_score': away_team_per_away_game_lost_score,
            'away_team_last_win_number_of_the_last_10_game': away_team_last_win_number_of_the_last_10_game,
            'away_team_rest_time_in_days': away_team_rest_time,
            'away_team_ranking_of_all_the_teams': away_team_ranking_of_all_the_teams,
            'away_team_away_win_rate': away_team_away_win_rate,
            'away_team_win_rate': away_team_win_rate,
            'how_long_after_season_begin' : how_long_after_season_begin_value,
            'home_win_or_lose': home_win_or_lose})
            

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

    print " --- use_win_rate_predict_correct accuracy: " + str(use_win_rate_predict_correct_count / 1000.0)

# usage: ~/workspace/nba_predict/my_oddsportal$ python -m my_oddsportal.tools.gen_per_team_per_game_features
if __name__=="__main__":
    meta_file_path = './data/meta/win_game-2017-2018'
    feature_csv_path = "./ml/game_features-2017-2018.csv"
    read_game_meta_file_and_output_features(meta_file_path, feature_csv_path)
