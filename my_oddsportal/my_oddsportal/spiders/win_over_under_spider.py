# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from scrapy_splash import SplashMiddleware
from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from my_oddsportal.items import WinNbaGame
import pickle
import re

OVER_UNDER_URL = "http://nba.win0168.com/odds/OverDown_n.aspx?id="

def get_game_ids(season):
    ret = []
    f = open('./data/win_game-' + season, 'r')
    count = 0

    while True:
        try:
            count = count + 1
            game = pickle.load(f)
            ret.append(game['game_id'])
        except EOFError:
            f.close()
            print(" --------- read " + str(count) + " games")
    return ret

class SplashSpider(Spider):
    season = "2017-2018"
    game_ids = get_game_ids(season)

    def start_requests(self):
        for game_id in self.game_ids:
            yield SplashRequest(OVER_UNDER_URL + game_id, self.parse, args = {'wait': '20'})
    
    def parse(self, response):
        

