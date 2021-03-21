import newspaper
from news import dump_all, save_to_db
from config import boards_path
import news 
import feedparser
# impoer newspaper
# news_df = dump_all(boards_path)
# save_to_db(news_df, db_path)

# print(news.download_board_news('https://tjournal.ru/rss/all')[['description']].to_string())

feed = feedparser.parse('https://tjournal.ru/rss/all')

# news_df = pd.DataFrame()

for entry in feed.entries:
    # try:
    # print(entry)
    # article = newspaper.Article(entry.link)
    # article.download()
    # article.parse()

    # # title = article.title
    print(entry.summary)

