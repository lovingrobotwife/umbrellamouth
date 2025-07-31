
import math
import random
import subprocess
from datetime import datetime, timedelta

from umbrellamouth import *

def split_name_and_args(x): 
    return x.split() 

def human_readable_timestamp(timestamp):
    dt = datetime.fromtimestamp(timestamp) # local (system) time
    return dt.strftime('%Y-%m-%d')

def timestamp_from_human_readable(x):
    dt = datetime.strptime(x, "%Y-%m-%d") # local (system) time
    return dt.timestamp()

def get_next_start_of_day():
    start_time = datetime.strptime(START_OF_DAY, '%H%M').time()

    now = datetime.now()
    next_start_of_day = datetime.combine(now.date(), start_time)

    if now.time() >= start_time:
        next_start_of_day += timedelta(days=1)
    
    return next_start_of_day

def call_scheduler(entry, attrs, ask=False):
    scheduler = attrs.get('scheduler', DEFAULT_SCHEDULER) 
    scheduler = split_name_and_args(scheduler)
    if ask: scheduler.append('--ask')
    proc = subprocess.run(scheduler, input=str(entry), text=True, capture_output=True)
    return proc.returncode

def remove_same_day_repetition(review_log):
    if not review_log: 
        return review_log
    today = datetime.now().date()
    last_review = datetime.fromtimestamp(review_log[-1][0]).date()
    if not last_review == today:
        return review_log
    review_log.pop()
    return review_log

def interval_(due_dt):
    diff = due_dt - get_next_start_of_day()
    diff_days = diff.total_seconds() / (24 * 3600)
    return math.ceil(diff_days)

# fuzz 

def gauss_fuzz(interval, ratio=0.2, min_interval=1, max_interval=36500):
    sigma = ratio * interval
    fuzzed = random.gauss(interval, sigma)
    fuzzed = max(min_interval, min(fuzzed, max_interval))
    return int(round(fuzzed))
