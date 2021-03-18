from news import dump_all, save_to_db
from config import boards_path

news_df = dump_all(boards_path)
# save_to_db(news_df, db_path)