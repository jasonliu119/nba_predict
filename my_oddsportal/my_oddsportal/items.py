# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class SplashTestItem(scrapy.Item):
    #单价
    price = scrapy.Field()
    # description = Field()
    #促销
    promotion = scrapy.Field()
    #增值业务
    value_add = scrapy.Field()
    #重量
    quality = scrapy.Field()
    #选择颜色
    color = scrapy.Field()
    #选择版本
    version = scrapy.Field()
    #购买方式
    buy_style=scrapy.Field()
    #套装
    suit =scrapy.Field()
    #增值保障
    value_add_protection = scrapy.Field()
    #白天分期
    staging = scrapy.Field()
    # post_view_count = scrapy.Field()
    # post_comment_count = scrapy.Field()
    # url = scrapy.Field()

class WinNbaGame(scrapy.Item):
    game_id = scrapy.Field()
    home = scrapy.Field()
    away = scrapy.Field()
    home_score = scrapy.Field()
    away_score = scrapy.Field()
    time = scrapy.Field()
    game_type = scrapy.Field()

class WinOverUnderItem(scrapy.Item):
    game_id = scrapy.Field()
    title = scrapy.Field()
    # the following fields are array [time, score, odd_over, odd_under, is_purple]
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
