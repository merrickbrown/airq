from flask import Flask, json, Response, render_template, g, request
import os, sys, datetime
from util import sensor_db

'''
TODO
[ ] Allow simple queries in the data API (eg location, date ranges)
[ ] Improve data response performance, right now we're looking at
[ ] Add 'start' endpoint for starting the logger with a particular location set, or changing the location during the run
[ ] Actually make index useful - eg display data, convenient UI for endpoints
[ ] Make this generally better, following model of, say https://flask.palletsprojects.com/en/1.1.x/tutorial/
'''

# shouldn't change the name
# seems to be used to set directories for web app, e.g. templates/
app = Flask(__name__)

@app.before_request
def before_request():
    g.db = sensor_db.connect()

@app.after_request
def after_request(response):
    if g.db is not None:
        g.db.close()
        g.db = None
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stop')
def stop_logger():
    if app.stop_logger is not None and not app.stop_logger.is_set():
        print('setting stop')
        app.stop_logger.set()
        return "Logger stopped"
    return "Logger not running"

@app.route('/data')
def data():
    #this is kinda slow - 10 sec for ~1 MB. My thinking is that if we chunk it out we can get
    # better performance
    # Mainly, just don't use jsonify - that is very slow
    # this is bad - also jjust assking for recent_days is broken
    args = request.args
    days = None
    hours = None
    if args.get("recent_days") is not None:
        try:
            days = int(args.get("recent_days"))
        except ValueError:
            pass
            # noop
    if args.get("recent_hrs") is not None:
        try:
            hours = int(args.get("recent_hrs"))
        except ValueError:
            pass
            # noop
    if days is not None and hours is None:
        hours = 0
    if days is None and hours is not None:
        days = 0
    if days is None and hours is None:
        days = 1
        hours = 0

    now = datetime.datetime.now()
    delta = datetime.timedelta(days=days, hours=hours)
    query = sensor_db.get_readings_in_date_range(
        g.db,
        start_date = now - delta,
        end_date = now,
        location = args.get('location'))

    # stream-based response generator
    def generate():
        readings = query.__iter__()
        # if it's empty: return the empty json
        try:
            prev = next(readings)
        except StopIteration:
            yield json.dumps({'records': []})
            raise StopIteration
        # it ain't empty - we can start pumping out the json record-by-record
        yield '{"records": ['
        for record in readings:
            # note: this is lagging - so it just yields the last value and stores the current
            yield json.dumps(prev) + ', '
            prev = record
        # close up the json
        yield json.dumps(prev) + ']}'

    return Response(generate(), status=200, mimetype="application/json")

def getApp(stop_event):
    app.stop_logger = stop_event
    return app

