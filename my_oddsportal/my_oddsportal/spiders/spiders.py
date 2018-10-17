# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from scrapy_splash import SplashMiddleware
from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from my_oddsportal.items import SplashTestItem
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = open('output.txt', 'w')

class SplashSpider(Spider):
    name = 'timestamps_and_game_links'
    # Valeurs pour 2013-2014
    # number_pages = 28 #29
    # start_url ="https://www.oddsportal.com/basketball/usa/nba-2008-2009/results/#/page/"
    # start_urls=[
    #     "https://www.oddsportal.com/basketball/usa/nba-2017-2018/golden-state-warriors-houston-rockets-fPfCQ1oq/#over-under;1",
    #     "https://www.oddsportal.com/basketball/usa/nba-2017-2018/golden-state-warriors-houston-rockets-fPfCQ1oq/#1X2;2",
    #     "https://www.oddsportal.com/basketball/usa/nba-2017-2018/golden-state-warriors-houston-rockets-fPfCQ1oq/#home-away;1",
    #     "https://www.oddsportal.com/basketball/usa/nba-2017-2018/golden-state-warriors-houston-rockets-fPfCQ1oq/#ah;1"]
    # for x in range(1, number_pages):
    #     start_urls.append(start_url + str(x))
    seasons = ['2017-2018']
    url_seasons = []
    page_count = [28]
    game_count = 0

    for i in range(len(seasons)):
        for j in range(page_count[i]):
            start_url = "https://www.oddsportal.com/basketball/usa/nba-" + seasons[i] + "/results/#/page/" + str(j + 1) + "/"
            url_seasons.append([start_url, seasons[i], j + 1])

    # request需要封装成SplashRequest
    def start_requests(self):
        for url_season in self.url_seasons:
            yield SplashRequest(url_season[0]
                                , self.parse
                                , args = {'wait': '10'}
                                , meta = {'season': url_season[1], "page": url_season[2]}
                                #,endpoint='render.json'
                                )

    def parse(self, response):
        # based on https://www.cnblogs.com/shaosks/p/6950358.html
        season = response.meta['season']
        page = response.meta['page']
        self.logger.info("********** parsing page " + str(page) + " of season " + season)

        site = Selector(response)
        timestamps = site.xpath('//*[@id="tournamentTable"]/tbody/tr[@class="odd deactivate"]/td[1]').extract()
        game_links = site.xpath('//*[@id="tournamentTable"]/tbody/tr[@class="odd deactivate"]/td[2]/a').extract()

        if len(timestamps) != len(game_links):
            self.logger.fatal("********** diff len of timestamps and game_links, %d v.s. %d", len(timestamps), len(game_links))
        else:
            self.logger.info("********** same len of timestamps and game_links, pased page %d, total games %d", page, len(game_links))

        with open('data/timestamps-' + season, 'a+') as f:
            for ts in timestamps:
                f.write(ts + "\n")

        with open('data/game_links-' + season, 'a+') as f:
            for link in game_links:
                f.write(link + "\n")

        self.game_count = self.game_count + len(timestamps)
        self.logger.info("********** so far parsed games: " + str(self.game_count)) 
