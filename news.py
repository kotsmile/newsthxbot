import re
import json
import random
import datetime

import pandas as pd
import feedparser
import newspaper

from db_manager import Database
from config import boards_path, db_path, is_online

pub_patterns = [
    '%a, %d %b %Y %H:%M:%S %z',
    '%a, %d %b %Y %H:%M:%S %Z',
    '%a, %d %b %Y %H:%M:%S'
]

def load_json(path):
    with open(path, 'r') as file:
        return json.load(file)

def download_board_news(rss):
    feed = feedparser.parse(rss)

    news_df = pd.DataFrame()
    
    for entry in feed.entries:
        try:
            print(entry)
            article = newspaper.Article(entry.link)
            article.download()
            article.parse()

            title = article.title
            try:
                description = entry.summary
            except AttributeError as e:
                article.nlp()
                description = article.summary
            link = entry.link
            img_link = article.top_image
            # Fri, 19 Mar 2021 12:14:07 +0300
            for pub_pattern in pub_patterns:
                try:
                    pub_date = datetime.datetime.strptime(entry.published, pub_pattern).strftime('%Y-%m-%d %H:%M')
                except ValueError:
                    continue
                break
            else:
                pub_date = entry.published
            
            news_df = news_df.append(pd.DataFrame({
                'title': [title],
                'description': [description],
                'link': [link],
                'img_link': [img_link],
                'pub_date': [pub_date]
            }))
        except AttributeError as e:
            print(e)
            continue

    return news_df


def dump_all(boards_path):
    news_df = pd.DataFrame()
    for board in load_json(boards_path):
        if board['enable']:
            board_news_df = download_board_news(rss=board['rss'])
            board_news_df['source'] = board['name']
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


def suggest_news_user(user_id):
    db = Database(db_path)
    fresh_news = db.get_fresh_news_for_user(user_id)
    if fresh_news.empty:
        print('Done!')
        return
    news_id = suggester(fresh_news, user_id)
    db.suggest_news(user_id, news_id)
        

def save_news():
    print('Start dumping')
    news_df = dump_all(boards_path)
    save_to_db(news_df, db_path)
    print('Done!')