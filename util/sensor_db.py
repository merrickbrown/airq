import dataset, os, pathlib, datetime

def connect():
    currentdir = pathlib.Path(os.path.realpath(__file__)).parent
    # potentially some opportunity to improve performance by passing some
    # sqlite engine options here
    return dataset.connect(f"sqlite:///{currentdir.parent}/data/sqlite/aq.db")

db = connect()

def db():
    return db

def insert_reading(db, location, reading):
    db.begin()
    try:
        locations = db['locations']
        locationEntity = locations.find_one(name=location)
        if locationEntity is None:
                locationEntity = {'name': location}
                locationEntity['id'] = locations.insert(locationEntity)
        readings = db['readings']
        reading_with_location = reading.copy()
        reading_with_location['location'] = locationEntity['name']
        reading_with_location['locationId'] = locationEntity['id']
        readings.insert(reading_with_location)
        db.commit()
        return True
    except Exception as ex:
        db.rollback()
        print(ex)
        return False
    
def get_readings_in_date_range(db, start_date, end_date = datetime.datetime.now(), location=None):
    table = db['readings']
    time_filter = {'between': (start_date, end_date)}
    if location is not None:
        return table.find(time=time_filter, location=location)
    else:
        return table.find(time=time_filter)
    
        
def get_readings(db, location = None):
    table = db['readings']
    # get all readings
    if location == None:
        return table.all()
    else:
        return table.find(location = location)
