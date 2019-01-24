# -*- coding: utf-8 -*-
import pickle
from ..items import WinOverUnderItem

game_id = '290090'
f = open('./data/over_under/2017-2018/{}.txt'.format(game_id), 'r')
count = 0

'''
class WinOverUnderItem(scrapy.Item):
    game_id = scrapy.Field()
    title = scrapy.Field()
    # the following fields are array [time, total score, odd_1, odd_2, is_after_game_start]
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

def dump(item, field):
    return ' ----- ' + field + ': ' + str(item[field])

while True:
    try:
        count = count + 1
        item = pickle.load(f)
        print(dump(item, 'game_id'))
        print(' ----- title: ' + item['title'])
        print(dump(item, 'macau'))
        print(dump(item, 'ysb8'))
        print(dump(item, 'crown'))
        print(dump(item, 'bet365'))
        print(dump(item, 'wade'))
        print(dump(item, 'sbo'))
    except EOFError:
        f.close()
        print(" --------- read " + str(count) + " WinOverUnderItem")
        break
