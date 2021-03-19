from news import dump_all, save_to_db
from config import boards_path
import news
# news_df = dump_all(boards_path)
# save_to_db(news_df, db_path)

print(news.download_board_news('https://www.vedomosti.ru/rss/news'))

