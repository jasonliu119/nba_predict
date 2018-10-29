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
import json

class SplashSpider(Spider):
    name = 'win_nba_games'
    seasons = [[2017, 2018]]
    months = [10, 11, 12, 1, 2, 3, 4]
    game_count = 0
    success_parsed_count = 0
    seasoned_urls = []
    # http://nba.win0168.com/cn/Normal.aspx?matchSeason=2017-2018&y=2017&m=12&SclassID=1
    base_url = "http://nba.win0168.com/cn/Normal.aspx?matchSeason={}-{}&y={}&m={}&SclassID=1"

    for i in range(len(seasons)):
        first_year = seasons[i][0]
        second_year = seasons[i][1]
        one_season_urls = []
        for j in range(len(months)):
            month = months[j]
            year = first_year
            if month < 10:
                year = second_year
            one_season_urls.append(base_url.format(first_year, second_year, year, month))
        seasoned_urls.append(one_season_urls)


    def start_requests(self):
        i = -1
        for one_season_urls in self.seasoned_urls:
            i = i + 1
            season_str = str(self.seasons[i][0]) + "-" + str(self.seasons[i][1])
            j = -1
            for one_month_url in one_season_urls:
                j = j + 1
                yield SplashRequest(one_month_url
                                    , self.parse
                                    , args = {'wait': '10'}
                                    , meta = {'season': season_str, "month": str(self.months[j])}
                                    #,endpoint='render.json'
                                    )

    def parse(self, response):
        season = response.meta['season']
        month = response.meta['month']
        self.logger.info("********** parsing month " + month + " of season " + season)

        site = Selector(response)
        games = site.xpath('//*[@id="scheTab"]/tbody/tr')

        for game_tr in games:
            game = WinNbaGame()
            game_type = game_tr.xpath('./td[1]').extract()
            type_normal = "常规赛"
            if type_normal.decode('utf-8') not in game_type[0]:
                self.logger.debug("date line " + game_type[0])
                continue
            game['game_type'] = game_type[0]
            game['game_id'] = game_type[0]
            game['home'] = game_type[0]
            game['away'] = game_type[0]
            game['final_score'] = game_type[0]
            game['time'] = game_type[0]
 
            with open('data/win_game-' + season, 'a+') as f:
                pickle.dump(game, f)
