from news import suggest_news, save_news
import schedule
import time
import datetime

from config import start_work, stop_work

def suggester():
    print('try to suggest news')
    if stop_work > datetime.datetime.now().time() > start_work:
        print('suggesting news')
        suggest_news()
def saver():
    print('try to add news')
    if stop_work > datetime.datetime.now().time() > start_work:
        print('adding news')
        save_news()

if __name__ == '__main__':
    print('Start')
    schedule.every(10).minutes.do(saver)
    schedule.every(20).minutes.do(suggester)
        
    while True:
        schedule.run_pending()
        time.sleep(10)