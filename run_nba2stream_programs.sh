echo "run nba predict crawl jobs"

cd nba_predict/my_oddsportal/

nohup python run_timed_check_program.py > check_program.log 2>check_program_error.log &
nohup python run_timed_meta_scrawl.py > meta.txt 2>meta_error.txt &
nohup python run_timed_tasks_before_game.py > before.txt 2>before_error.txt &

cd ../../nba_stream/

nohup python run_timed_generate_index_html.py /home/ubuntu/ > generate_index.txt 2>generate_index_error.txt &

