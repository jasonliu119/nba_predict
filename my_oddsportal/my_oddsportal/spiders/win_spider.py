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

STATS_URL_PATTERN = re.compile('.*matchid=(\d+)')

def get_game_id(url):
    return STATS_URL_PATTERN.match(url).group(1)

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
            f = open('data/win_game-' + season_str, 'wb')
            j = -1
            for one_month_url in one_season_urls:
                j = j + 1
                yield SplashRequest(one_month_url
                                    , self.parse
                                    , args = {'wait': '20'}
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
            game_type_td = game_tr.xpath('./td[1]')
            game_type = game_type_td.xpath('./text()').extract()
            if len(game_type) == 0:
                self.logger.debug("date line " + game_type_td.extract()[0])
                continue
            type_normal = "常规赛"
            if type_normal.decode('utf-8') not in game_type[0]:
                self.logger.debug("date line " + game_type[0])
                continue
            game['game_type'] = game_type[0]

            time_str = game_tr.xpath('./td[2]/text()').extract()[0]
            game['time'] = time_str

            home = game_tr.xpath('./td[3]/a/text()').extract()[0]
            game['home'] = home

            stats_url = game_tr.xpath('./td[4]/a/@href').extract()[0]
            game['game_id'] = get_game_id(stats_url)

            away = game_tr.xpath('./td[5]/a/text()').extract()[0]
            game['away'] = away

            home_score = game_tr.xpath('./td[4]/a/span[1]/text()').extract()[0]
            game['home_score'] = home_score

            away_score = game_tr.xpath('./td[4]/a/span[2]/text()').extract()[0]
            game['away_score'] = away_score
 
            with open('data/win_game-' + season, 'a+') as f:
                pickle.dump(game, f)
