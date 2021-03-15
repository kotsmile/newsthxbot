import json
import os, sys
from numpy import ERR_IGNORE

import requests
import pandas as pd
from lxml import etree

from db_manager import DB

boards_path = os.path.join(sys.path[0], 'boards.json')
db_path = os.path.join(sys.path[0], '..', 'news.db')

def read_boards(boards_path):
    boards = []
    with open(boards_path, 'r') as boards_file:
        boards = json.load(boards_file)
    return boards

def download_rss(rss):
    response = requests.get(rss)
    if response.status_code == 200:
        xml = response.text
        items = etree.fromstring(xml).xpath('//item')
        rss = []
        
        for item in items:
            article = {}
            for child in item:
                print(child.tag)
                print(child.text)
                if 'url' in child.attrib:
                    article['imgLink'] = child.attrib['url']
                else:
                    article[child.tag] = child.text
            rss.append(article)
        return rss

    return None

def dump_all(boards_path, fields=['title', 'link', 'imgLink', 'description', 'pubDate']):
    boards = read_boards(boards_path)
    news_df = pd.DataFrame()
    for board in boards:
        rss = download_rss(board['rss'])
        for news in rss:
            news['source'] = board['name']
            news_df = news_df.append(news, ignore_index=True)

    news_df = news_df[['source'] + fields]
    return news_df


def save_to_db(news_df, db_path):
    db = DB(db_path)
    connection = db.connection
    news_df.to_sql('temp_news', con=connection, if_exists='replace', index=False)
    cur = connection.cursor()
    q = f'insert or ignore into news ({", ".join(news_df.columns)}) select {", ".join(news_df.columns)} from temp_news'
    cur.execute(q)
    connection.commit()
    connection.close()



