from flask import Flask, json, Response, g
import os, sys
from util import sensor_db

app = Flask("AirQ Sensor data")

@app.route('/')
def index():
    return 'Hello world'

@app.route('/stop')
def stop_logger():
    if app.stop_logger is not None and not app.stop_logger.is_set():
        print('setting stop')
        app.stop_logger.set()
        return "Logger stopped"
    return "Logger not running"
    

@app.route('/data')
def data():
    res = []
    # we can safely use connect here because under the hood datasets uses a connection pool
    db = sensor_db.connect()
    # this should be replaced with a generator, but json-ing the result can be a bit tricky
    # see https://blog.al4.co.nz/2016/01/streaming-json-with-flask/ for some ideas
    for record in sensor_db.get_readings(db):
        res.append(record)
    # don't use jsonify here it is way too slow
    body = json.dumps({'records': res})
    print(f"Returned {len(res)} records")
    return Response(response=body, status=200, mimetype="application/json")

def getApp(stop_event):
    app.stop_logger = stop_event
    return app
    