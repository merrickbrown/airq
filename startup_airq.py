#!/usr/bin/python3

import socket, os, sys, argparse
from multiprocessing import Process, Event
# this sucks I hate this, probably means I should restructure the
# project or just learn how to use modules correctly
currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(currentdir)
sys.path.append(currentdir + '/util')
import aq_to_db 
from webapp import app 

# Main entry point for server + logger

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def server_info():
    return f"http://{get_ip_address()}:5000"

def run_webapp(stop_event = None, debug = True):
    # setting use_reloader to True (default) will cause multi-process code to not work great
    app.getApp(stop_event).run(use_reloader=False, debug=debug, host='0.0.0.0')

def run_logger(stop_event = None, location='Unknown'):
    aq_to_db.log_readings(stop_event, location = location)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-c', '--location', help='location to use for logging', default="Unknown")
    p.add_argument('-s', '--no-server', help='flag to not start the webserver', action='store_true')
    p.add_argument('-g', '--no-logger', help='flag to not start the logger', action='store_true')
    p.add_argument('-d', '--no-debug', help='flag to not start the webserver in debug mode', action = 'store_true')
    args = p.parse_args()
    
    stop_event = Event()
    server_p = Process(
        target = run_webapp,
        kwargs = {
            'debug': not args.no_debug,
            'stop_event': stop_event})
    logger_p = Process(
        target = run_logger,
        kwargs = {'location': args.location,
            'stop_event': stop_event})
    
    if not args.no_server:
        server_p.start()
        print("Visible on network as: " + server_info())
        print(f"Server PID: {server_p.pid}")
    if not args.no_logger:
        logger_p.start()
        print(f"Logger PID: {logger_p.pid}")
    if not args.no_server:
        server_p.join()
    if not args.no_logger:
        logger_p.join()
        
