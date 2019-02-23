import scrapy
from scrapy import Request
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from scrapy_splash import SplashMiddleware
from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from my_oddsportal.items import WinNbaGame
from scrapy import Selector
import pickle
import re
from sets import Set
from ..tools.send_message import send_email, send_sms

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

NBA_STREAM = 'https://nba-stream.com/next-games-live/'

TIME_OUT = 1800.0

GAME_DIV = "broadcastOfEvent"

def get_game_file_name(url):
    '''
    01 Celtics
    02 Nets
    03 Knicks
    04 76ers
    05 Raptors
    06 Warriors
    07 Clippers
    08 Lakers
    09 Suns
    10 Kings
    11 Bulls
    12 Cavaliers
    13 Pistons
    14 Pacers
    15 Bucks
    16 Hawks
    17 Hornets
    18 Heat
    19 Magic
    20 Wizards
    21 Nuggets
    22 Timberwolves
    23 Thunder
    24 Trail Blazers
    25 Jazz
    26 Mavericks
    27 Rockets
    28 Grizzlies
    29 Pelicans
    30 Spurs
    '''

    teams = Set()
    url = url.lower()
    cities = [
        'boston', 'brooklyn', 'york', 'philadelphia', 'toronto',
        'golden','clipper','laker','Phoenix','Sacramento',
        'chicago','Cleveland','Detroit','Indiana','Milwaukee',
        'Atlanta','Charlotte', 'miami','orlando','washington',
        'denver','minnesota','Oklahoma','Portland','Utah',
        'Dallas','houston','Memphis','Orleans','Antonio']
    names = [
        'Celtic', 'Net', 'Knick', '76er', 'Raptor',
        'Warrior','clipper','laker','Sun','King',
        'Bull','Cavalier','Piston','Pacer','Buck',
        'Hawk','Hornet', 'Heat','Magic','Wizard',
        'Nugget','Timberwol','Thunder','Blazer','Jazz',
        'Maverick','Rocket','Grizzl','Pelican','Spur']
    import datetime
    now = datetime.datetime.now()
    i = 0
    for city in cities:
        i += 1
        if city.lower() in url:
            teams.add(i)
    i = 0
    for name in names:
        i += 1
        if name.lower() in url:
            if name.lower() == 'net' and 'hornet' in url:
                continue
            teams.add(i)

    # for net and hornet
    if len(teams) < 2:
        net_i = url.find('net')
        hornet_i = url.find('hornet')
        if net_i >= 0 and hornet_i >= 0 and net_i != hornet_i:
            teams.add(2)
            teams.add(17)

    if (len(teams) != 2):
        print '.....teams ' + str(teams)
        links = url.split('/')
        return "./data/game_links/{}/{}.txt".format(now.strftime("%Y-%m-%d"), "b-error-" + str(links[len(links) - 1]))

    team_list = list(teams)
    small = str(min(team_list))
    big = str(max(team_list))
    if len(small) == 1:
        small = '0' + small
    if len(big) == 1:
        big = '0' + big

    return "./data/game_links/{}/b-{}-{}.txt".format(now.strftime("%Y-%m-%d"), small, big)

def create_dir(filename):
    import os
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

script = """
function main(splash)
  splash.private_mode_enabled = false
  local url = splash.args.url
  assert(splash:go(url))
  assert(splash:wait(10))
  return {
    html = splash:html(),
    png = splash:png(),
    har = splash:har(),
  }
end
"""

def get_month_day_from_epoch(epoch):
    la_tz = 'America/Los_Angeles'
    from datetime import datetime
    import pytz
    # get time in UTC
    utc_dt = datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.utc)
    # convert it to tz
    tz = pytz.timezone(la_tz)
    dt = utc_dt.astimezone(tz)
    return dt.month, dt.day

class SplashSpider(Spider):
    name = 'nba_streams'
    count = 0

    def start_requests(self):
        yield SplashRequest(NBA_STREAM
            , self.parse
            , endpoint='execute'
            , cache_args=['lua_source']
            , args = {'timeout': TIME_OUT, 'wait': '30', 'lua_source': script})

    def parse(self, response):
        site = Selector(response)
        ff = open('test-NBA_STREAM' + '.txt', 'wb')
        ff.write(response.text)

        games = site.xpath("//div[contains(@itemprop, '{}')]".format(GAME_DIV))

        for game in games:
            # print "game itemprop " + game.xpath('./@itemprop').extract()[0]
            try:
                first_game_link_a = game.xpath('./a[1]')

                # based on the title to decide whether it is an NBA game
                first_title = first_game_link_a.xpath("./@title").extract()[0]
                second_title = first_game_link_a.xpath("./b/text()").extract()[0]
                filename = get_game_file_name(first_title)
                if 'error' in filename:
                    filename = get_game_file_name(second_title)
                if 'error' in filename:
                    continue
                create_dir(filename)

                # only write down today's games
                data_timestamp = game.xpath("./time/span/@data-time").extract()[0]
                epoch = int(data_timestamp) / 1000
                data_month, data_day = get_month_day_from_epoch(epoch)
                import time
                current = int(time.time())
                current_month, current_day = get_month_day_from_epoch(current)

                game_link = first_game_link_a.xpath("./@href").extract()[0]
                print "got data_month {}, data_day {}, game_link: {}".format(data_month, data_day, game_link)
                if current_month == data_month and current_day == data_day:
                    f = open(filename, 'wb')
                    f.write(second_title + "\n" + game_link + "\n")
                    print "write to file " + filename + "\n"

            except Exception as e:
                print "Error, continue: " + str(e)
                continue


        