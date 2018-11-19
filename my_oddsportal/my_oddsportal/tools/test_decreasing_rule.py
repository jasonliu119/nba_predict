# -*- coding: utf-8 -*-

import pickle
from ..items import WinNbaGame

f = open('./data/meta/win_game-2017-2018', 'r')
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

from ..items import WinOverUnderItem

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

import time

def to_timestamp(time_str):
    return time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M"))

def is_decreasing(scores_odds):
    ts_score = {}
    for item in scores_odds:
        if item[4]: # is_purple
            continue

        timestamp = to_timestamp(item[0])
        score = item[1]
        ts_score[timestamp] = score
    ts_array = ts_score.keys()
    ts_array.sort()
    prev_score = 500
    for ts in ts_array:
        if prev_score < ts_score[ts]:
            return False, 0
        prev_score = ts_score[ts]
    return True, prev_score

def dump(item, field):
    return ' ----- ' + field + ': ' + str(item[field])

count = 0
dec_count = 0
meta_missing = 0
bet365_dec_and_under_count = 0
sbo_dec_and_under_count = 0
ysb8_dec_and_under_count = 0

game_id = '290495'
# f = open('./data/over_under/2017-2018/{}.txt'.format(game_id), 'r')
directory = './data/over_under/2017-2018/'
cur_id = 0
import os
for filename in os.listdir(directory):
    if filename == 'error_games_file.txt':
        continue

    f = open('./data/over_under/2017-2018/{}'.format(filename), 'r')

    try:
        item = pickle.load(f)
        count = count + 1

        is_dec_bet365, score_bet365 = is_decreasing(item['bet365'])

        # is_dec_wade, score_wade = is_decreasing(item['wade'])
        is_dec_sbo, score_sbo = is_decreasing(item['sbo'])
        is_dec_ysb8, score_ysb8 = is_decreasing(item['ysb8'])
        cur_id = int(item['game_id'])

        if cur_id not in dict_id_score:
            print " --- meta missing " + item['game_id']
            meta_missing = meta_missing + 1

        final_score = dict_id_score[cur_id]

        if is_dec_bet365 and is_dec_sbo and is_dec_ysb8:
            dec_count = dec_count + 1
            if final_score < score_bet365:
                bet365_dec_and_under_count = bet365_dec_and_under_count + 1
            if final_score < score_sbo:
                sbo_dec_and_under_count = sbo_dec_and_under_count + 1
            if final_score < score_ysb8:
                ysb8_dec_and_under_count = ysb8_dec_and_under_count + 1
            print " ---- is_decreasing " + item['game_id']

    except:
        f.close()
        print 'exception ' + str(cur_id)

print(" --------- read totally " + str(count) + " WinOverUnderItem")
print(" --------- read " + str(meta_missing) + " meta_missing")
print(" --------- read " + str(dec_count) + " dec_count")
print(" --------- read " + str(bet365_dec_and_under_count) + " bet365_dec_and_under_count")
print(" --------- read " + str(sbo_dec_and_under_count) + " sbo_dec_and_under_count")
print(" --------- read " + str(ysb8_dec_and_under_count) + " ysb8_dec_and_under_count")


