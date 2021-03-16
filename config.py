import os, sys
import datetime

boards_path = os.path.join(sys.path[0], 'files/boards.json')
creds_path = os.path.join(sys.path[0], 'files/creds.json')
db_path = os.path.join(sys.path[0], 'db/newsthx.db')

start_work = datetime.time(hour=9, minute=0, second=0)
stop_work = datetime.time(hour=21, minute=0, second=0)