import time, datetime, board, busio, sched, argparse
import pandas as pd
from device import getPM25

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

def read_row():
    # We've got to copy this over since it seems that the read() returns a reference to the dict.
    aqdata = getPM25().read().copy()
    aqdata['time'] = [datetime.datetime.now()]
    return aqdata.copy()

'''
This blocks, should be used in a thread/process if used outside this script
'''
def avg_readings(period_s = 20, num_samples = 10):
    data = []
    delta = period_s/num_samples
    for i in range(num_samples):
        try:
            row = read_row()
            data.append(row)
        except RuntimeError:
            print("Could not read from PM2.5")
        # bad, constant delta-based sampling. use a timer that self corrects each iteration
        # instead
        time.sleep(delta)
    avg = avg_dicts(data).to_dict()
    # set the time to be the last time we sampled
    avg['time'] = datetime.datetime.now()
    return avg