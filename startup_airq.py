#!/usr/bin/env python3

import socket, os, sys, argparse
from multiprocessing import Process, Event
from util import aq_to_db
import webapp

# Main entry point for server + logger
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def server_info():
    return f"http://{get_ip_address()}:5000"

'''
Run the web app. The passed in 'stop_event' allows the web server to signal to the
logger process to stop running.
'''
def run_webapp(stop_event = None, debug = True):
    # setting use_reloader to True (default) will cause multi-process code to not work great
    webapp.getApp(stop_event).run(use_reloader=False, debug=debug, host='0.0.0.0')

'''
Run the logger process, logging readings with the passed in location string.
The passed in 'stop_event' allows the web server to signal to the logger process to stop running.
'''
def run_logger(stop_event = None, location='Unknown'):
    # infinite loop until stop event is triggered
    aq_to_db.log_readings(stop_event, location = location)
    print("Logger stopped")

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-c', '--location', help='location to record in each record when logging', default="Unknown")
    p.add_argument('-s', '--no-server', help='flag to not start the webServer', action='store_true')
    p.add_argument('-g', '--no-logger', help='flag to not start the loGger', action='store_true')
    p.add_argument('-d', '--no-debug', help='flag to not start the webserver in Debug mode', action = 'store_true')

    args = p.parse_args()

    start_server = not args.no_server
    start_logger = not args.no_logger
    debug = not args.no_debug

    # events are basically safe booleans we can use to pass information between processes
    stop_event = Event()
    server_p = Process(
        target = run_webapp,
        kwargs = {
            'debug': debug,
            'stop_event': stop_event})
    logger_p = Process(
        target = run_logger,
        kwargs = {'location': args.location,
            'stop_event': stop_event})

    if start_server:
        server_p.start()
        print("Visible on network as: " + server_info())
        print(f"Server PID: {server_p.pid}")

    if start_logger:
        logger_p.start()
        print(f"Logger PID: {logger_p.pid}")

    # join these, probably not totally necessary
    # but as an upshot, allows us to ^C this script to send the
    # KeyboardInterrupt to both child processes
    if start_server:
        server_p.join()
    if start_logger:
        logger_p.join()
