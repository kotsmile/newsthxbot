from news import suggest_news, save_news
import schedule
import time
import datetime

from config import start_work, stop_work


if __name__ == '__main__':
    print('try to add news')
    if stop_work > datetime.datetime.now().time() > start_work:
        print('adding news')
        save_news()
        suggest_news()
        # prod
        schedule.every(10).minutes.do(save_news)
        schedule.every(20).minutes.do(suggest_news)
    
    while True:
        schedule.run_pending()
        time.sleep(10)