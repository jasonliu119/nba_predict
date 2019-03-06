# nba_predict

# 阅读历史数据
（1）首先，你要pip install Scrapy. More details: https://doc.scrapy.org/en/latest/intro/install.html<br />
（2）目前有两种历史数据：meta数据 和 over-under数据<br />
（3）meta数据的定义是在nba_predict/my_oddsportal/my_oddsportal/items.py的 WinNbaGame，包含一场历史比赛的基本信息。<br />

```bash
# example code to read the meta data 
# data path: ./data/meta/win_game-2017-2018
cd nba_predict/my_oddsportal/
python -m my_oddsportal.tools.dump_game_meta
```

(3）over-under数据的定义是在nba_predict/my_oddsportal/my_oddsportal/items.py的 WinOverUnderItem。<br />
这个数据包含了一场比赛的6个庄家的赔率变化数据。每个庄家都是一个list，list的每个元素是一个list，[time, score, odd_over, odd_under, is_after_game_start]，
分别是：该赔率出现时间、总分盘口、大分赔率、小分赔率、是否是开赛后赔率。<br />

比如在某个时刻，总分盘口是200，大分赔率是0.9，小分赔率是0.8，意思是在这个时刻，如果我押100块在大分，最后结果的确大分（两队得分总和超过200），我可以拿回190块；如果我押100块在小分，最后结果是小分，我拿回180块。<br />
目前我只研究is_after_game_start=False的数据，就是开赛前的数据，因为开赛后赔率变化很快、波动大，不容易分析。

```bash
# example code to read the over-under data 
# data path: ./data/over_under/2017-2018/{}.txt
cd nba_predict/my_oddsportal/
python -m my_oddsportal.tools.dump_over_under
```


# How to run crawler

Run splash with docker:
sudo docker run -p 8050:8050 scrapinghub/splash --max-timeout 3600

Run predict:
sh run_decreasing_rule_with_seeds.sh "325987 325988 325989 325990"

Dump game meta:
python -m my_oddsportal.tools.dump_game_meta

Crawl:
scrapy crawl win_nba_games

pip install twilio

# Run in background
in nba_predict:
nohup python run_timed_check_program.py > check_program.log 2>check_program_error.log &
nohup python run_timed_meta_scrawl.py > meta.txt 2>meta_error.txt &
nohup python run_timed_tasks_before_game.py > before.txt 2>before_error.txt &
in nba_stream:
nohup python run_timed_generate_index_html.py > generate_index.txt 2>generate_index_error.txt &


