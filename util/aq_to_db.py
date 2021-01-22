import sensor_db, argparse, os
from aq import avg_readings

def log_reading(db, location):
    row = avg_readings()
    return sensor_db.insert_reading(db, location, row)

def log_readings(stop_event, location = 'Unknown'):
    count = 0
    while stop_event is not None and not stop_event.is_set():
        try:
            if log_reading(sensor_db.connect(), location):
                count += 1
        except KeyboardInterrupt:
            break
    print(f"Added {count} new records.")
