# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from scrapy_splash import SplashMiddleware
from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from my_oddsportal.items import WinOverUnderItem
import pickle
import re
import os

#  scrapy crawl win_over_under

IS_TEST = False

season = "2018-2019" # 2017-2018

OVER_UNDER_URL = "http://nba.win0168.com/odds/OverDown_n.aspx?id="

def create_dir_if_not_exist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_game_ids():
    ret = []
    f = open('./data/win_game-' + season, 'r')
    count = 0

    while True:
        try:
            count = count + 1
            if IS_TEST and count > 5:
                break
            game = pickle.load(f)
            ret.append(game['game_id'])
        except EOFError:
            f.close()
            print(" --------- read " + str(count) + " games")
            break
    return ret

def get_specified_game_ids():
    ret = []
    ret.append('325673')
    ret.append('325661')
    ret.append('325623')
    ret.append('325666')
    ret.append('325675')
    ret.append('325682')
    ret.append('325690')
    ret.append('325696')
    ret.append('325698')
    ret.append('325700')
    ret.append('325701')
    ret.append('325705')
    ret.append('325706')
    ret.append('325709')
    ret.append('325720')
    ret.append('325724')
    ret.append('325725')
    ret.append('325729')
    ret.append('325730')
    ret.append('325750')
    ret.append('325751')
    ret.append('325759')
    ret.append('325760')
    ret.append('325773')
    ret.append('325777')
    ret.append('325781')
    return ret

class SplashSpider(Spider):
    name = 'win_over_under'
    # game_ids = get_game_ids()
    # game_ids = get_specified_game_ids()
    game_ids = []
    over_under_dir = ''
    error_games_file = None

    def __init__(self, seed_ids=None, output_dir=None, *args, **kwargs):
        super(SplashSpider, self).__init__(*args, **kwargs)

        if output_dir == None:
            self.over_under_dir = './data/over_under/' + season + '/'
        else:
            self.over_under_dir = output_dir + '/' + season + '/'

        create_dir_if_not_exist(self.over_under_dir)
        error_games_file = open(self.over_under_dir + 'error_games_file.txt', 'wb')

        if seed_ids == None:
            self.game_ids = get_specified_game_ids()
        else:
            self.game_ids = seed_ids.split()

    def start_requests(self):
        for game_id in self.game_ids:
            yield SplashRequest(OVER_UNDER_URL + game_id, self.parse, args = {'timeout': 1800, 'wait': '20'},
                meta = {'game_id': game_id})
    
    def parse(self, response):
        game_id = response.meta['game_id']
        self.logger.info("********** parsing game_id " + game_id)

        def get_maker(index):
            if index == 1:
                return 'macau'
            if index == 2:
                return 'ysb8'
            if index == 3:
                return 'crown'
            if index == 4:
                return 'bet365'
            if index == 5:
                return 'wade'
            if index == 6:
                return 'sbo'
            return 'invalid-maker'

        def get_odds(odds_str):
            p = re.compile('([\.\d]+)[^\.\d]+([\.\d]+)')
            r = p.match(odds_str)
            return [r.group(1), r.group(2)]

        try:
            item = WinOverUnderItem()
            item['game_id'] = game_id
            # init the dict
            for i in range(6):
                index = i + 1
                maker = get_maker(index)
                item[maker] = []

            site = Selector(response)
            item['title'] = site.xpath('/html/body/table[1]/tbody/tr/td/text()').extract()[0]

            rows = site.xpath('/html/body/table[3]/tbody/tr')
            first = True
            for row in rows:
                if first:
                    # First row is head line
                    first = False
                    continue
                time = row.xpath('./td[7]/text()').extract()[0]
                for i in range(6):
                    # odds fields are array [time, score, odd_1, odd_2, is_purple]
                    index = i + 1
                    cell = row.xpath('./td[' + str(index) + ']')
                    score_xpath = cell.xpath('./span')
                    if not score_xpath:
                        continue
                    maker = get_maker(index)
                    score = cell.xpath('./span/text()').extract()[0]

                    is_purple = False
                    if cell.xpath('./@style'):
                        color = cell.xpath('./@style').extract_first()
                        is_purple = (color == 'background-color: #CCCCEE')

                    odds_str = cell.xpath('./text()').extract_first()
                    odds = get_odds(odds_str)
                    # add to the maker dict
                    item[maker].append([time, score, odds[0], odds[1], is_purple])

                    with open(self.over_under_dir + game_id + '.txt', 'wb') as one_game_over_under:
                        pickle.dump(item, one_game_over_under)
        except Exception as e:
            line = " --------- crawl win_over_under game_id " + game_ids + " error: %s" % str(e)
            error_games_file.write(line + '\n')
            print(line)


