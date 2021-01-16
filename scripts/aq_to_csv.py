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
def avg_dicts(dicts):
    collected = {}
    for d in dicts:
        for k,v in d.items():
            if k in collected:
                collected[k].append(v)
            else:
                collected[k] = [v]
    df = pd.DataFrame(collected)
    return df.mean()  

def read_row(pm25):
    # We've got to copy this over since it seems that the read() returns a reference to the dict.
    aqdata = pm25.read().copy()
    aqdata['time'] = [datetime.datetime.now()]
    return aqdata.copy()

'''
This is currently blocking - which I think is OK small values of period, but
that can be fixed by using some threading here
'''
def avg_readings(pm25, period_s = 2, num_samples = 50):
    data = []
    delta = period_s/num_samples
    for i in range(num_samples):
        try:
            row = read_row(pm25)
            data.append(row)
        except RuntimeError:
            print("Could not read from PM2.5")
        time.sleep(delta)
    avg = avg_dicts(data)
    # set the time to be the last time we sampled
    avg['time'] = pd.Timestamp(datetime.datetime.now())
    return avg

def save_aq(pm25, file, first = False):
    d = pd.DataFrame(read_row(pm25), index=[0])
    if first:
        d.columns = d.columns.str.replace(r'\s+', '_')
        write = lambda f : d.to_csv(f, index = False)
    else:
        write = lambda f : d.to_csv(f, mode='a',
        header=False, index=False)
    try:
        print(write(file))
    except IOException as ex:
        print('IOException: ' + ex.message)
    except Exception as ex:
        print(ex) 
   
print(avg_readings(pm25).to_csv(index = False))
'''
# INITIALIZE
dt = datetime.datetime.now().timetuple()
file = f"{args.filepre}_{dt[2]}{dt[1]}{dt[0]}.csv"
save_aq(pm25, file, first = True)

# RUN
s = sched.scheduler()

for i in range(1, args.N+1):
   s.enter(args.s*i, 1, save_aq, kwargs={'pm25': pm25, 'file': file})

s.run()
'''