"""
Write to csv all output from PM25 sensor
every s seconds, a total N times
default is 60 seconds, 900 times (15h) 
to be scheduled in crontab (defaults and naming  suggest daily)

modified from the example
https://github.com/adafruit/Adafruit_CircuitPython_PM25/blob/master/examples/pm25_simpletest.py

TODO: 
[X] append to csv at intermittent times (every time?) so if killed not all data is lost
[] try statements and error handling: sometimes the process dies unexpectedly (failure to read from device? see circuitpy_test files for evidence of it being possible)
[] add option to append to existing csv, instead of writing to filepre_dmy.csv
[] cleaner schedule handling and interface between filenaming, crontab, python scheduler, rtcwake
[] checks against stupidity? e.g. N*s longer period than cron interval
"""

import time, datetime, board, busio, sched, argparse
import pandas as pd
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C

p = argparse.ArgumentParser()
p.add_argument('--filepre', help='file name prefix relative to current wd, filepre_dmy.csv', default="")
p.add_argument('--s', type=int, help='interval in seconds read from PM2.5', default=60)
p.add_argument('--N', type=int, help='N intervals to read', default=900)

args = p.parse_args()

# DEVICE READER
reset_pin = None
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
pm25 = PM25_I2C(i2c, reset_pin)

# FUN
def save_aq(pm25, file, first = False):
    aqdata = pm25.read()
    aqdata['time'] = datetime.datetime.now()
    if first:
        d = pd.DataFrame(aqdata, index=[0])
        d.columns = d.columns.str.replace(r'\s+', '_')
        d.to_csv(file, index = False)
    else:
        pd.DataFrame(aqdata, index = [0]).to_csv(file, mode='a',
        header=False, index=False)

# INITIALIZE
dt = datetime.datetime.now().timetuple()
file = f"{args.filepre}_{dt[2]}{dt[1]}{dt[0]}.csv"
save_aq(pm25, file, first = True)

# RUN
s = sched.scheduler()

for i in range(1, args.N+1):
   s.enter(args.s*i, 1, save_aq, kwargs={'pm25': pm25, 'file': file})

s.run()
