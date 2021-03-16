import re
import json

import requests
import pandas as pd
import random

from db_manager import Database
from config import boards_path, db_path

def load_json(path):
    with open(path, 'r') as file:
        return json.load(file)

def download_board_news(board):
    # title, description, imgLink, link, pubDate
    response = requests.get(board['rss'])
    board_news_df = pd.DataFrame()
    if response.status_code == 200:

        xml = response.text.replace('\n', '')
        regexs = board['regexs']
        for tag, regex in regexs.items():
            board_news_df[tag] = pd.Series(re.findall(regex, xml))
            
        board_news_df['source'] = board['name']

    return board_news_df

def dump_all(boards_path):
    news_df = pd.DataFrame()
    for board in load_json(boards_path):
        board_news_df = download_board_news(board)
        news_df = news_df.append(board_news_df, ignore_index=True)

    return news_df


def save_to_db(news_df, db_path):
    db = Database(db_path)
    connection = db.connection

    news_df.to_sql('temp_news', con=connection, if_exists='replace', index=False)

    insert_q = f'insert or ignore into news ({", ".join(news_df.columns)}) select {", ".join(news_df.columns)} from temp_news'
    db.insert_query(insert_q)

    update_q = 'update news set is_new = 0 where link not in (select link from temp_news);'
    db.insert_query(update_q)


def suggester(news, user_id):
    return random.choice(news['id'])

def suggest_news():
    print('Suggesting')
    db = Database(db_path)
    users_df = db.get_users()

    for id, row in users_df.iterrows():
        user_id = row['id']
        fresh_news = db.get_fresh_news_for_user(user_id)
        if fresh_news.empty:
            print('Done!')
            return
        
        news_id = suggester(fresh_news, user_id)
        db.suggest_news(user_id, news_id)
        
    print('Done')


def save_news():
    print('Start dumping')
    news_df = dump_all(boards_path)
    save_to_db(news_df, db_path)
    print('Done!')