import time
import os
from datetime import datetime

def crawl_meta_every(t):
    while True:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " starts crawling game meta")
        os.system('scrapy crawl win_nba_games') # crawl the game meta data of the year
        time.sleep(t)

if __name__ == '__main__':
    crawl_meta_every(24 * 2 * 3600)
