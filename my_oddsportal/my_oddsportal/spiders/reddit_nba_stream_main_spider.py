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

REDDIT = 'https://www.reddit.com/'
REDDIT_NBA_STREAM_MAIN = 'https://www.reddit.com/r/nbastreams/'

# page types
TYPE_MAIN = "main"
TYPE_GAME = "game"
TYPE_LINK = "link"

TIME_OUT = 1800.0

MAIN_GAME_DIV_CLASS = "SQnoC3ObvgnGjWt90zD9Z"
GAME_TABLE_CLASS = "s90z9tc-19 iDFCDm"
GAME_LINK_CLASS = "usertext-body may-blank-within md-container"

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

    if (len(teams) != 2):
        print '.....teams ' + str(teams)
        links = url.split('/')
        return "./data/game_links/{}/{}.txt".format(now.strftime("%Y-%m-%d"), "error-" + str(links[len(links) - 1]))

    team_list = list(teams)
    small = str(min(team_list))
    big = str(max(team_list))
    if len(small) == 1:
        small = '0' + small
    if len(big) == 1:
        big = '0' + big

    return "./data/game_links/{}/{}-{}.txt".format(now.strftime("%Y-%m-%d"), small, big)

def create_dir(filename):
    import os
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def get_game_file_name_from_2_source(link, site, response):
    filename = get_game_file_name(link)
    if "error" in filename:
        # f = open("./test.txt", "wb")
        # f.write(response.text)
        tittle = site.xpath("//head/title/text()").extract()[0]
        filename = get_game_file_name(tittle)
    if "error" in filename:
        print("wrong team names in reddit spider: " + filename)
    return filename

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

script1 = """
function main(splash)
    local num_scrolls = 10
    local scroll_delay = 1.0

    local scroll_to = splash:jsfunc("window.scrollTo")
    local get_body_height = splash:jsfunc(
        "function() {return document.body.scrollHeight;}"
    )
    assert(splash:go(splash.args.url))
    splash:wait(splash.args.wait)

    for _ = 1, num_scrolls do
        scroll_to(0, get_body_height())
        splash:wait(scroll_delay)
    end        
    return splash:html()
end
"""

script2 = """
function scroll_to(splash, x, y)
  local js = string.format(
    "window.scrollTo(%s, %s);", 
    tonumber(x), 
    tonumber(y)
  )
  return splash:runjs(js)
end


function get_doc_height(splash)
  return splash:runjs([[
    Math.max(
        Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
        Math.max(document.body.offsetHeight, document.documentElement.offsetHeight),
        Math.max(document.body.clientHeight, document.documentElement.clientHeight)
    )
  ]])
end


function scroll_to_bottom(splash)
  local y = get_doc_height(splash)
  return scroll_to(splash, 0, y)
end


function main(splash)

  -- e.g. http://infiniteajaxscroll.com/examples/basic/page1.html
  local url = splash.args.url
  assert(splash:go(url))
  assert(splash:wait(0.5))
  splash:stop()
  
  for i=1,10 do
    scroll_to_bottom(splash)    
    assert(splash:wait(0.2))
  end

  splash:set_viewport("full")

  return {
    html = splash:html(),
    png = splash:png{width=640},
    har = splash:har(),
  }
end
"""

class SplashSpider(Spider):
    name = 'reddit_main'
    count = 0

    def start_requests(self):
        yield SplashRequest(REDDIT_NBA_STREAM_MAIN
            , self.parse
            , endpoint='execute'
            , cache_args=['lua_source']
            , args = {'timeout': TIME_OUT, 'wait': '30', 'lua_source': script}
            , meta = {'type': TYPE_MAIN})

    def parse(self, response):
        site = Selector(response)
        type_meta = response.meta['type']
        print "in parse, got type: " + type_meta

        if type_meta == TYPE_MAIN:
            ff = open('test-TYPE_MAIN-' + '.txt', 'wb')
            
            ff.write(response.text)
            games = site.xpath("//a[contains(@class, '{}')]".format(MAIN_GAME_DIV_CLASS))
            for game in games:
                self.count = self.count + 1
                link = game.xpath('./@href').extract()[0]
                tittle = game.xpath('./h2/text()').extract()[0]
                print " -- No." + str(self.count) + " " + tittle + " " + link

                if "Game Thread:" in tittle:
                    print " -- Game Thread No." + str(self.count) + ", from main page: game link: " + link + ", tittle: " + tittle + "\n\n"
                    yield SplashRequest(REDDIT + link
                        , self.parse
                        , args = {'timeout': TIME_OUT, 'wait': '30'}
                        , meta = {'type': TYPE_GAME, 'link': link})
        elif type_meta == TYPE_GAME:
            filename = get_game_file_name_from_2_source(response.meta['link'], site, response)
            create_dir(filename)
            f = open(filename, 'wb')
            tables = site.xpath('//table')

            for table in tables:
                text_link = table.xpath('./thead/tr/th[2]/text()').extract()
                if len(text_link) > 0:
                    if text_link[0].strip() == 'Link':
                        rows = table.xpath("./tbody/tr")
                        for row in rows:
                            link = row.xpath('./td[2]/a/@href').extract()[0]
                            text = row.xpath('./td[2]/a/text()').extract()[0]

                            if 'r/nbastreams' in link:
                                yield SplashRequest(REDDIT + link
                                    , self.parse
                                    , args = {'timeout': TIME_OUT, 'wait': '30'}
                                    , meta = {'type': TYPE_LINK, 'filename': filename})
                            else:
                                f.write(text + "\n" + link + "\n")
        elif type_meta == TYPE_LINK:
            # ff = open('test-page-' + str(self.count) + '.txt', 'wb')
            # self.count = self.count + 1
            # ff.write(response.text)
            filename = response.meta['filename']
            create_dir(filename)
            f = open(filename, 'a')

            a_xpath = "//*[contains(@id, 'form-t1_')]/div/div/p/a"
            games = site.xpath(a_xpath)
            for game in games:
                link = game.xpath('./@href').extract()[0]
                print " -- parsed link " + link
                tittle = game.xpath('./text()').extract()[0]
                f.write(tittle + "\n" + link + "\n")


        