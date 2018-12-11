#!/bin/bash

seed_ids=$1 # e.g, '325673'

seed_output='./data/seed_ids/'
echo "rm -R ${seed_output}"

rm -R ${seed_output}

echo "scrapy crawl win_over_under -a seed_ids=${seed_ids} -a output_dir=${seed_output}"

scrapy crawl win_over_under -a seed_ids="${seed_ids}" -a output_dir=${seed_output}

echo "python -m my_oddsportal.tools.run_decreasing_rule ${seed_output}2018-2019/ no-final"

python -m my_oddsportal.tools.run_decreasing_rule ${seed_output}2018-2019/ no-final
