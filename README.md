# nba_predict

Run splash with docker:
sudo docker run -p 8050:8050 scrapinghub/splash

Run predict:
sh run_decreasing_rule_with_seeds.sh "325987 325988 325989 325990"

Dump game meta:
python -m my_oddsportal.tools.dump_game_meta

Crawl:
scrapy crawl win_nba_games

pip install twilio

