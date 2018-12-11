# -*- coding: utf-8 -*-

import pickle
from ..items import WinNbaGame
from sets import Set

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

dict_id_score[325673] = 189
dict_id_score[325661] = 211
dict_id_score[325623] = 188
dict_id_score[325666] = 227
 
dict_id_score[325675] = 239
dict_id_score[325682] = 201
dict_id_score[325690] = 212
dict_id_score[325696] = 208
dict_id_score[325698] = 220
dict_id_score[325700] = 184
dict_id_score[325701] = 204
dict_id_score[325705] = 203
dict_id_score[325706] = 219
dict_id_score[325709] = 192
dict_id_score[325720] = 215
dict_id_score[325724] = 199
dict_id_score[325725] = 181
dict_id_score[325729] = 176
dict_id_score[325730] = 205
dict_id_score[325750] = 197
dict_id_score[325751] = 216
dict_id_score[325759] = 194
dict_id_score[325760] = 213
dict_id_score[325773] = 217
dict_id_score[325777] = 210
dict_id_score[325781] = 186

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

def is_decreasing_base(scores_odds):
    ts_score = {}
    for item in scores_odds:
        if item[4]: # is_purple
            continue

        timestamp = to_timestamp(item[0])
        ts_score[timestamp] = float(item[1])
    ts_array = ts_score.keys()
    ts_array.sort()
    prev_score = 500
    for ts in ts_array:
        if prev_score < ts_score[ts]:
            return False, 0
        prev_score = ts_score[ts]
    return True, prev_score

# allow a few times of increasing
def is_decreasing_type_2(scores_odds, allow_inc = 5, delta = 2):
    ts_score = {}
    is_purple = 0
    for item in scores_odds:
        if item[4]: # is_purple
            is_purple = is_purple + 1
            continue

        timestamp = to_timestamp(item[0])
        ts_score[timestamp] = float(item[1])
    ts_array = ts_score.keys()
    ts_array.sort()
    prev_score = 500
    inc = 0
    max_score = 0
    min_score = prev_score
    for ts in ts_array:
        if prev_score < ts_score[ts]:
            inc = inc + 1
        prev_score = ts_score[ts]
        if prev_score > max_score:
            max_score = prev_score
        if prev_score < min_score:
            min_score = prev_score
    # print " inc " + str(inc)
    try:
        first_ts = ts_array[0]
    except:
        print "is_purple: " + str(is_purple)
        print "scores_odds len: " + str(len(scores_odds))
    last_ts = ts_array[len(ts_array) - 1]
    if ts_score[first_ts] - ts_score[last_ts] >= delta:
        # print " inc " + str(inc)
        if inc > allow_inc:
                return False, 0
        return True, prev_score
    return False, 0

def is_decreasing_type_3(scores_odds, allow_inc = 6, delta = 2):
    ts_score = {}
    is_purple = 0
    for item in scores_odds:
        if item[4]: # is_purple
            is_purple = is_purple + 1
            continue

        timestamp = to_timestamp(item[0])
        ts_score[timestamp] = float(item[1])

    # all purple
    if len(ts_score) < 2:
        return False, 0, 0

    ts_array = ts_score.keys()
    ts_array.sort()
    prev_score = 500
    inc = 0
    max_score = 0
    min_score = prev_score
    first_dec_ts = 0
    for ts in ts_array:
        print "-- ts: " + str(ts) + ", -- score: " + str(ts_score[ts])
        if prev_score < ts_score[ts]:
            inc = inc + 1
            if inc > allow_inc:
                return False, 0, 0
        elif first_dec_ts == 0 and prev_score > ts_score[ts] and prev_score != 500:
            first_dec_ts = ts
        prev_score = ts_score[ts]
        if prev_score > max_score:
            max_score = prev_score
        if prev_score < min_score:
            min_score = prev_score
    # print " inc " + str(inc)
    first_ts = ts_array[0]
    last_ts = ts_array[len(ts_array) - 1]
    if ts_score[first_ts] > ts_score[last_ts] and max_score > min_score:
        # print " inc " + str(inc)
        if inc > allow_inc:
                return False, 0, 0
        return True, prev_score, first_dec_ts
    return False, 0, 0

def is_decreasing(scores_odds, default = False):
    if len(scores_odds) == 0:
        return default, 500, 2540910220.0, False

    score_set = Set()
    last_score = 0.0
    for item in scores_odds:
        if item[4]: # is_purple
            continue

        score_set.add(item[1])
        last_score = float(item[1])

    if len(score_set) == 1:
        return True, last_score, 2540910220.0, False

    a, b, c = is_decreasing_type_3(scores_odds)
    return a, b, c, True

def dump(item, field):
    return ' ----- ' + field + ': ' + str(item[field])

def dump_game(item):
    print("-------------------------------")
    print(dump(item, 'game_id'))
    print(' ----- title: ' + item['title'])
    print(dump(item, 'macau'))
    print(dump(item, 'ysb8'))
    print(dump(item, 'crown'))
    print(dump(item, 'bet365'))
    print(dump(item, 'wade'))
    print(dump(item, 'sbo'))

# f = open('./data/over_under/2017-2018/{}.txt'.format(game_id), 'r')

cur_id = 0
import os
import sys

def run_decreasing_rule(directory, check_final_score=True):
    all_dec_list = []
    not_all_dec_list = []

    count = 0
    all_dec_count = 0

    all_dec_bet365_under = 0
    all_dec_wade_under = 0
    all_dec_sbo_under = 0
    all_dec_ysb8_under = 0

    meta_missing = 0

    bet365_dec_count = 0
    wade_dec_count = 0
    sbo_dec_count = 0
    ysb8_dec_count = 0

    bet365_dec_and_under_count = 0
    wade_dec_and_under_count = 0
    sbo_dec_and_under_count = 0
    ysb8_dec_and_under_count = 0

    for filename in os.listdir(directory):
        if filename == 'error_games_file.txt':
            continue

        f = open((directory + '{}').format(filename), 'r')

        item = pickle.load(f)
        count = count + 1

        print " === bet365:"
        is_dec_bet365, score_bet365, first_ts_bet365, from_algo_bet365 = is_decreasing(item['bet365'])
        print " === wade:"
        is_dec_wade, score_wade, first_ts_wade, from_algo_wade = is_decreasing(item['wade'], True)
        print " === sbo:"
        is_dec_sbo, score_sbo, first_ts_sbo, from_algo_sbo = is_decreasing(item['sbo'])
        print " === ysb8:"
        is_dec_ysb8, score_ysb8, first_ts_ysb8, from_algo_ysb8 = is_decreasing(item['ysb8'])

        cur_id = int(item['game_id'].strip())

        print "first_ts_bet365: " + str(first_ts_bet365)
        print "first_ts_wade: " + str(first_ts_wade)
        print "first_ts_sbo: " + str(first_ts_sbo)
        print "first_ts_ysb8: " + str(first_ts_ysb8)

        if check_final_score and cur_id not in dict_id_score:
            print " --- meta missing " + item['game_id']
            meta_missing = meta_missing + 1

        if not from_algo_bet365 and not from_algo_wade:
            continue

        if not from_algo_sbo and not from_algo_ysb8:
            continue

        final_score = 0
        if check_final_score:
            final_score = dict_id_score[cur_id]

        if is_dec_bet365:
            bet365_dec_count = bet365_dec_count + 1
            if final_score < score_bet365:
                bet365_dec_and_under_count = bet365_dec_and_under_count + 1

        if is_dec_wade:
            wade_dec_count = wade_dec_count + 1
            if final_score < score_wade:
                wade_dec_and_under_count = wade_dec_and_under_count + 1

        if is_dec_sbo:
            sbo_dec_count = sbo_dec_count + 1
            if final_score < score_sbo:
                sbo_dec_and_under_count = sbo_dec_and_under_count + 1

        if is_dec_ysb8:
            ysb8_dec_count = ysb8_dec_count + 1
            if final_score < score_ysb8:
                ysb8_dec_and_under_count = ysb8_dec_and_under_count + 1

        #  min(first_ts_sbo, first_ts_ysb8) > min(first_ts_wade, first_ts_bet365)
        if is_dec_bet365 and is_dec_sbo and is_dec_ysb8 and is_dec_wade and min(first_ts_sbo, first_ts_ysb8) > min(first_ts_wade, first_ts_bet365):
            all_dec_count = all_dec_count + 1
            all_dec_list.append(item["game_id"])
            if final_score < score_bet365:
                all_dec_bet365_under = all_dec_bet365_under + 1
            if final_score < score_wade:
                all_dec_wade_under = all_dec_wade_under + 1
            if final_score < score_sbo:
                all_dec_sbo_under = all_dec_sbo_under + 1
            if final_score < score_ysb8:
                all_dec_ysb8_under = all_dec_ysb8_under + 1
        else:
            not_all_dec_list.append(item["game_id"]);

            #print " ---- is_decreasing " + item['game_id']

    print(" --------------------------- ")
    print(" --------- read " + str(bet365_dec_count) + " bet365_dec_count")
    print(" --------- read " + str(wade_dec_count) + " wade_dec_count")
    print(" --------- read " + str(sbo_dec_count) + " sbo_dec_count")
    print(" --------- read " + str(ysb8_dec_count) + " ysb8_dec_count")
    print(" --------------------------- ")
    if check_final_score:
        print(" --------- read " + str(bet365_dec_and_under_count) + " bet365_dec_and_under_count")
        print(" --------- read " + str(wade_dec_and_under_count) + " wade_dec_and_under_count")
        print(" --------- read " + str(sbo_dec_and_under_count) + " sbo_dec_and_under_count")
        print(" --------- read " + str(ysb8_dec_and_under_count) + " ysb8_dec_and_under_count")

    print(" --------- read totally " + str(count) + " WinOverUnderItem")
    print(" --------- read " + str(meta_missing) + " meta_missing")
    print(" --------- read " + str(all_dec_count) + " all_dec_count")

    if check_final_score:
        print(" --------- read " + str(all_dec_bet365_under) + " all_dec_bet365_under")
        print(" --------- read " + str(all_dec_wade_under) + " all_dec_wade_under")
        print(" --------- read " + str(all_dec_sbo_under) + " all_dec_sbo_under")
        print(" --------- read " + str(all_dec_ysb8_under) + " all_dec_ysb8_under")

    print("=======================")
    for id in all_dec_list:
        print " ----- match min rule: " + str(id)

    for id in not_all_dec_list:
        print " ----- not match min rule: " + str(id)

def main():
    # directory = './data/over_under/2017-2018/'
    directory_default = './data/over_under/2018-2019/'
    directory = ''

    check_final_score = True
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        if len(sys.argv) > 2:
            check_final_score = False
    else:
        directory = directory_default

    run_decreasing_rule(directory, check_final_score)

if __name__ == "__main__":
    main()

# 325661 ysb no change
# 


