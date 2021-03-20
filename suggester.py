from news import suggest_news, save_news
import schedule
import time
import json

from config import start_work, stop_work, params_path, is_online

def suggester():
    print('try to suggest news')
    if is_online():
        print('suggesting news')
        suggest_news()
def saver():
    print('try to add news')
    if is_online():
        print('adding news')
        save_news()

if __name__ == '__main__':
    every_mins = json.load(open(params_path, 'r'))['every']
    print('Start')
    schedule.every(10).minutes.do(saver)
    schedule.every(every_mins).minutes.do(suggester)
        
    while True:
        schedule.run_pending()
        time.sleep(10)