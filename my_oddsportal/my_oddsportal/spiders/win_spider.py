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
    # seasons = [[2017, 2018]]
    # months = [10, 11, 12, 1, 2, 3, 4]
    seasons = [[2018, 2019]]

    import os
    for season in seasons:
        file_name = 'data/meta/win_game-' + str(season[0]) + "-" + str(season[1])
        if os.path.exists(file_name):
            os.remove(file_name)

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
                                    , args = {'timeout': 1800, 'wait': '30'}
                                    , meta = {'season': season_str, "month": str(self.months[j])}
                                    #,endpoint='render.json'
                                    )

    def log_error(self, path, ):
        with open(path, 'a+') as f:
            f.write(msg)

    def parse(self, response):
        def get_first_if_any(array):
                if array is not None and len(array) > 0:
                    return array[0]
                return "0";

        def get_game_id(analysis):
            # e.g., analysis/325991.htm
            if analysis is not None and len(analysis) > 0:
                analysis_url = analysis[0]
                if analysis_url.strip() == '':
                    return "0"

                import re
                ret = re.findall(r"\d{6}", analysis_url)
                if len(ret) == 1:
                    return ret[0]
            return "0"

        season = response.meta['season']
        directory = 'data/meta/'
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
            # timezone different:
            # crawler: time 12-02 00:00, id 290166, home 奥兰多魔术, away 金州勇士
            # v.s.
            # web: time 12-01 17:00
            game['time'] = time_str

            home = game_tr.xpath('./td[3]/a/text()').extract()[0]
            game['home'] = home

            game['game_id'] = get_game_id(game_tr.xpath('./td[8]/a[1]/@href').extract())

            away = game_tr.xpath('./td[5]/a/text()').extract()[0]
            game['away'] = away

            home_score = get_first_if_any(game_tr.xpath('./td[4]/a/span[1]/text()').extract())
            game['home_score'] = home_score

            away_score = get_first_if_any(game_tr.xpath('./td[4]/a/span[2]/text()').extract())
            game['away_score'] = away_score

            with open(directory + '/win_game-' + season, 'a+') as f:
                pickle.dump(game, f)
