import time

def to_timestamp(time_str):
    return time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M"))

def is_decreasing(scores_odds):
    ts_score = {}
    for item in scores_odds:
        if item[4]: # is_purple
            continue

        timestamp = to_timestamp(item[0])
        score = item[1]
        ts_score[timestamp] = score
    ts_array = ts_score.keys()
    ts_array.sort()
    prev_score = 500
    for ts in ts_array:
        if prev_score < ts_score[ts]:
            return False, 0
        prev_score = ts_score[ts]
    return True, prev_score

# <time, total score, odd_1, odd_2, is_purple>
# 2018-02-01 07:05

def test_is_decreasing(a):
    result, score = is_decreasing(a)
    print " result " + str(result)
    print " score " + str(score)

# false
a1 = [
    ["2018-02-01 07:05", 100, 1, 1, False], 
    ["2018-02-01 06:05", 99, 1, 1, False],
    ["2018-02-01 07:06", 99, 1, 1, False],
    ["2018-02-02 07:06", 98, 1, 1, False]]

# test_is_decreasing(a1)

# true
a2 = [
    ["2018-02-01 07:05", 100, 1, 1, False], 
    ["2018-02-01 06:05", 99, 1, 1, True],
    ["2018-02-01 07:06", 99, 1, 1, False],
    ["2018-02-02 07:06", 98, 1, 1, False]]

# test_is_decreasing(a1)

# false
a3 = [
    ["2018-04-01 07:05", 100, 1, 1, False], 
    ["2018-02-01 06:05", 99, 1, 1, True],
    ["2018-02-03 06:06", 101, 1, 1, False],
    ["2018-02-02 05:06", 102, 1, 1, False]]

# test_is_decreasing(a1)

def is_decreasing_type_2(scores_odds, allow_inc = 3):
    ts_score = {}
    for item in scores_odds:
        if item[4]: # is_purple
            continue

        timestamp = to_timestamp(item[0])
        score = item[1]
        ts_score[timestamp] = score
    ts_array = ts_score.keys()
    ts_array.sort()
    prev_score = 500
    inc = 0
    max_score = 0
    min_score = prev_score
    for ts in ts_array:
        if prev_score < ts_score[ts]:
            inc = inc + 1
        prev_score = ts_score[ts]
        if prev_score > max_score:
            max_score = prev_score
        if prev_score < min_score:
            min_score = prev_score
    print " inc " + str(inc)

    first_ts = ts_array[0]
    last_ts = ts_array[len(ts_array) - 1]
    if min_score == ts_score[last_ts] and max_score == ts_score[first_ts]:
        
        if inc > allow_inc:
                return False, 0
        return True, prev_score
    return False, 0

def test_is_decreasing_2(a):
    result, score = is_decreasing_type_2(a)
    print " result " + str(result)
    print " score " + str(score)

test_is_decreasing_2(a1)

test_is_decreasing_2(a2)

test_is_decreasing_2(a3)