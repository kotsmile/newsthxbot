import os, sys
import datetime
import json
import datetime

boards_path = os.path.join(sys.path[0], 'files/boards.json')
creds_path = os.path.join(sys.path[0], 'files/creds.json')
params_path = os.path.join(sys.path[0], 'files/params.json')
db_path = os.path.join(sys.path[0], 'db/newsthx.db')

# add auto time zone

start_work = lambda: datetime.datetime.strptime(json.load(open(params_path, 'r'))['start'], '%H:%M:%S').time()
stop_work = lambda: datetime.datetime.strptime(json.load(open(params_path, 'r'))['stop'], '%H:%M:%S').time()


def is_online():
    return stop_work() > datetime.datetime.now().time() > start_work()