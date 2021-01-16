"""
Write to csv all output from PM25 sensor
every s seconds, a total N times
default is 60 seconds, 900 times (15h) 
to be scheduled in crontab (defaults and naming  suggest daily)

modified from the example
https://github.com/adafruit/Adafruit_CircuitPython_PM25/blob/master/examples/pm25_simpletest.py

TODO: 
[X] append to csv at intermittent times (every time?) so if killed not all data is lost
[x] try statements and error handling: sometimes the process dies unexpectedly (failure to read from device? see circuitpy_test files for evidence of it being possible)
[] add option to append to existing csv, instead of writing to filepre_dmy.csv
[] cleaner schedule handling and interface between filenaming, crontab, python scheduler, rtcwake
[] checks against stupidity? e.g. N*s longer period than cron interval
"""

import time, datetime, board, busio, sched, argparse
import pandas as pd
from device import getPM25
from aq import read_row

def save_aq(d, file, first = False):
    if first:
        d.columns = d.columns.str.replace(r'\s+', '_')
        write = lambda f : d.to_csv(f, index = False)
    else:
        write = lambda f : d.to_csv(f, mode='a', header=False, index=False)
    try:
        write(file)
    except IOException as ex:
        print('IOException: ' + ex.message)
    except Exception as ex:
        print(ex) 

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--filepre', help='file name prefix relative to current wd, filepre_dmy.csv', default="")
    p.add_argument('--s', type=int, help='interval in seconds read from PM2.5', default=60)
    p.add_argument('--N', type=int, help='N intervals to read', default=900)
    p.add_argument('--append', type=bool, help='whether to append to existing file or not', default=False) 

    args = p.parse_args()

    # INITIALIZE
    dt = datetime.datetime.now().timetuple()
    file = f"{args.filepre}_{dt[2]}{dt[1]}{dt[0]}.csv"
        
    def read_and_save_aq(file, first = False):
        save_aq(pd.DataFrame(read_row(), index=[0]), file, first)
    
    read_and_save_aq(file, first = True)

    # RUN
    s = sched.scheduler()

    for i in range(1, args.N+1):
       s.enter(args.s*i, 1, read_and_save_aq, kwargs={'file': file})
    s.run()
