import dataset, os, pathlib

def connect():
    currentdir = pathlib.Path(os.path.realpath(__file__)).parent
    return dataset.connect(f"sqlite:///{currentdir.parent}/data/sqlite/aq.db")

db = connect()

def db():
    return db

def insert_reading(db, location, reading):
    db.begin()
    try:
        table = db['readings']
        reading_with_location = reading.copy()
        reading_with_location['location'] = location
        table.insert(reading_with_location)
        db.commit()
    except:
        db.rollback()
        
def get_readings(db, location = None):
    table = db['readings']
    # get all readings
    if location == None:
        return table.all()
    else:
        return table.find(location = location)