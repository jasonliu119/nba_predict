# -*- coding: utf-8 -*-

import pickle
from ..items import WinNbaGame
from ..items import WinOverUnderItem
import time

season = '2017-2018'
f = open('./data/meta/win_game-' + season, 'r')
count = 0

dict_id_score = {}

while True:
    try:
        count = count + 1
        game = pickle.load(f)
        dict_id_score[int(game['game_id'])] = int(game['home_score']) + int(game['away_score'])
    except EOFError:
        f.close()
        print(" --------- read " + str(count) + " games")
        break

#################################################################################################
directory = './data/over_under/2017-2018/'
cur_id = 0

dealers = ['bet365', 'wade', 'sbo', 'ysb8']

file_name = 'data/win_game_features-' + season + '.txt'
file = open(file_name, 'wb')

def to_timestamp(time_str):
    return time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M"))

'''
class WinOverUnderItem(scrapy.Item):
    game_id = scrapy.Field()
    title = scrapy.Field()
    # the following fields are array <time, total score, odd_1, odd_2, is_purple>
    # 澳门
    macau = scrapy.Field()
    # 易胜博
    ysb8 = scrapy.Field()
    # 皇冠
    crown = scrapy.Field()
    # bet365
    bet365 = scrapy.Field()
    # 韦德
    wade = scrapy.Field()
    # 利记
    sbo = scrapy.Field()
'''
# return [last, first, max, min, average, dec_times, inc_times, dec_delta_sum, inc_delta_sum, len]
def get_features(scores_odds):
    ts_score = {}
    is_purple = 0
    for item in scores_odds:
        if item[4]: # is_purple
            is_purple = is_purple + 1
            continue

        timestamp = to_timestamp(item[0])
        ts_score[timestamp] = float(item[1])

    if len(ts_score) == 0:
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    ts_array = ts_score.keys()
    ts_array.sort()

    last = ts_score[ts_array[len(ts_array) - 1]]
    first = ts_score[ts_array[0]]
    max_score = -1.0
    min_score = 1000
    sum_score = 0.0
    dec_times = 0
    inc_times = 0
    dec_delta_sum = 0.0
    inc_delta_sum = 0.0
    prev = -1
    for ts in ts_array:
        cur_score = ts_score[ts]
        if cur_score > max_score:
            max_score = cur_score
        if cur_score < min_score:
            min_score = cur_score
        sum_score += cur_score

        if prev > 0:
            if prev > cur_score:
                dec_times = dec_times + 1
                dec_delta_sum = dec_delta_sum + prev - cur_score
            elif prev < cur_score:
                inc_times = inc_times + 1
                inc_delta_sum = inc_delta_sum + cur_score - prev
        prev = cur_score

    return [last, first, max_score, min_score, sum_score / len(ts_array), dec_times, inc_times, dec_delta_sum, inc_delta_sum, len(ts_array)] 

import os
meta_missing = 0
done = 0
features_missing = 0
results = {}
for filename in os.listdir(directory):
    if filename == 'error_games_file.txt':
        continue
    f = open((directory + '{}').format(filename), 'r')
    item = pickle.load(f)
    count = count + 1
    cur_id = int(item['game_id'].strip())
    if cur_id not in dict_id_score:
        print " --- meta missing " + item['game_id']
        meta_missing = meta_missing + 1
    final_score = dict_id_score[cur_id]
    final_over_count = 0

    for dealer in dealers:
        features = get_features(item[dealer])
        with open(file_name, 'a+') as f:
            for feature in features:
                f.write(str(feature) + ' ')
            f.write('\n')
            if not features[0] > 0:
                f.write('0\n')
                features_missing = features_missing + 1
            elif features[0] > final_score:
                f.write('-1\n')
                final_over_count = final_over_count - 1
            elif features[0] <= final_score:
                f.write('1\n')
                final_over_count = final_over_count + 1

    done = done + 1
    if final_over_count not in results.keys():
        results[final_over_count] = 1
    else:
        results[final_over_count] = 1 + results[final_over_count]

print "---meta_missing: " + str(meta_missing)
print "---features_missing: " + str(features_missing)
print "---done: " + str(done)
print "---results: " + str(results)