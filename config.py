import datetime
import json
import os
import sys

boards_path = os.path.join(sys.path[0], 'files/boards.json')
creds_path = os.path.join(sys.path[0], 'files/creds.json')
params_path = os.path.join(sys.path[0], 'files/params.json')
db_path = os.path.join(sys.path[0], 'db/newsthx.db')

# add auto time zone

def is_online():
    start_work = datetime.datetime.strptime(json.load(open(params_path, 'r'))['start'], '%H:%M:%S %z').time()
    stop_work = datetime.datetime.strptime(json.load(open(params_path, 'r'))['stop'], '%H:%M:%S %z').time()
    return stop_work > datetime.datetime.now().time() > start_work
