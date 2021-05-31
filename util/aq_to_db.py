# import sensor_db, argparse, os
import argparse, os
from .aq import avg_readings
from . import sensor_db

def log_reading(db, location):
    row = avg_readings()
    return sensor_db.insert_reading(db, location, row)

def log_readings(stop_event, location = 'Unknown'):
    count = 0
    ## let's hold the db connection
    db = sensor_db.connect()
    while stop_event is not None and not stop_event.is_set():
        try:
            if log_reading(db, location):
                count += 1
        except KeyboardInterrupt:
            break
    print(f"Added {count} new records.")
    db.close()
