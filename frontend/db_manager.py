import sqlite3
import pandas as pd

from config import db_path


class Database:

    def __init__(self, path):
        self.path = path
    
    @staticmethod
    def connect_db(path):
        try:
            conn = sqlite3.connect(path)
            return conn
        except Exception as e:
            print(e)
            return None

    @property
    def connection(self):
        return Database.connect_db(self.path)
    
    def select_query(self, q):
        connection = self.connection
        return pd.read_sql_query(q, connection)

    def insert_query(self, q):
        connection = self.connection
        cur = connection.cursor()
        cur.execute(q)
        connection.commit()
        connection.close()



db = Database(db_path)

def is_notify(user_id):
    is_notify_df = db.select_query(f"select * from users where id = '{user_id}' and notify = 1")
    return not is_notify_df.empty

def is_exist(user_id):
    is_exist_df = db.select_query(f"select * from users where id = '{user_id}'")
    return not is_exist_df.empty

def is_admin(user_id):
    is_admin_df = db.select_query(f"select * from users where id = '{user_id}' and is_admin = 1")
    return not is_admin_df.empty

def set_notify(user_id, notify):
    db.insert_query(f"update users set notify = {notify} where id = '{user_id}'")

def get_fresh_news(user_id):
    news_for_user_q = f"select news_id from suggested_news  where user_id = '{user_id}' and seen = 0 order by timestamp desc limit 1 "
    news_for_user = db.select_query(news_for_user_q)
    if not news_for_user.empty:
        news_id = news_for_user.iloc[0][0]
        get_news_q = f"select id, title, description, link, img_link from news where id = {news_id}"
        news_data = db.select_query(get_news_q)
        if not news_data.empty:
            news_data = news_data.iloc[0]
            db.insert_query(f"update suggested_news set seen = 1 where user_id = '{user_id}' and news_id = {news_data['id']}")
            return news_data['id'], news_data['title'], news_data['description'], news_data['link'], news_data['img_link']
    return -1, -1, -1, -1, -1


