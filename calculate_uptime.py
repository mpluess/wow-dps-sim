import glob
import os
import re
import statistics

BUFF = 'Dragonspine Trophy'
LOG_DIR = 'logs'
LOG_PREFIX = '20220112-1411'

TIME_REGEX = re.compile(r'^\[(\d+\.\d+)\] ')
BUFF_START_REGEX = re.compile(rf'{BUFF} Proc$')
BUFF_END_REGEX = re.compile(rf'{BUFF} Proc fades$')
uptimes = []
for path_to_log in glob.iglob(os.path.join(LOG_DIR, f'{LOG_PREFIX}*.txt')):
    current_time = None
    buff_start_time = None
    buff_start_end_times = []
    with open(path_to_log, encoding='utf-8') as f:
        for line in f:
            time_regex_match = TIME_REGEX.search(line)
            if time_regex_match is not None:
                current_time = float(time_regex_match.group(1))
                buff_start_match = BUFF_START_REGEX.search(line)
                if buff_start_match is not None:
                    assert buff_start_time is None
                    buff_start_time = current_time
                else:
                    buff_end_match = BUFF_END_REGEX.search(line)
                    if buff_end_match is not None:
                        assert buff_start_time is not None
                        buff_start_end_times.append((buff_start_time, current_time))
                        buff_start_time = None

        if buff_start_time is not None:
            buff_start_end_times.append((buff_start_time, current_time))

    uptime = sum(end - start for start, end in buff_start_end_times) / current_time
    uptimes.append(uptime)

print(statistics.mean(uptimes))
