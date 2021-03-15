from news import suggest_news, save_news
import schedule
import time

if __name__ == '__main__':
    save_news()
    suggest_news()
    # prod
    # schedule.every(10).minutes.do(save_news)
    # schedule.every(20).minutes.do(suggest_news)
    
    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)