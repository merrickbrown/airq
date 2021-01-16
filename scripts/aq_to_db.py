import sensor_db, argparse
from aq import avg_readings

db = sensor_db.connect()

def log_reading(db, location):
    row = avg_readings()
    return sensor_db.insert_reading(db, location, row)

def log_readings(db, location):
    count = 0
    while True:
        try:
            print(log_reading(db, location))
        except KeyboardInterrupt:
            print(f"Added {count} new records.")

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--location', help='Location to use for this reading', default="Unknown")
    args = p.parse_args()

    log_readings(db, args.location)