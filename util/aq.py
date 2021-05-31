import time, datetime
# import asyncio to convert some of these to non-blocking.
# overall, I am not 100% if that is truly necessary since this is all in one process
# Main benefits I can see are to allow better combination of sampling + averaging, also something like a current readings tracker
# could be neat as part of a dashboard or something
import pandas as pd
from .device import getPM25

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

def avg_readings(period_s = 60, num_samples = 15):
    data = []
    delta = period_s/num_samples
    for i in range(num_samples):
        try:
            row = read_row()
            data.append(row)
        except RuntimeError:
            print("Could not read from PM2.5")
        # bad, constant, delta-based sampling. use a timer that self corrects each iteration
        # instead
        time.sleep(delta)
    avg = avg_dicts(data).to_dict()
    # set the time to be the last time we sampled
    avg['time'] = datetime.datetime.now()
    return avg

    
