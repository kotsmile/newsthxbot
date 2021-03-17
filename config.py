import os, sys
import datetime

boards_path = os.path.join(sys.path[0], 'files/boards.json')
creds_path = os.path.join(sys.path[0], 'files/creds.json')
db_path = os.path.join(sys.path[0], 'db/newsthx.db')

# add auto time zone
start_work = datetime.time(hour=7, minute=0, second=0)
stop_work = datetime.time(hour=18, minute=0, second=0)