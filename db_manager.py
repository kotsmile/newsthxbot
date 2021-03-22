import sqlite3

import pandas as pd

create_news_table_q = '''
create table if not exists  news
(
    id integer primary key autoincrement,
    source text not null,
    title text not null,
    link text not null unique,
    img_link text not null,
    description text not null,
    pub_date text not null,
    is_new integer default 1
);
'''
create_temp_news_table_q = '''
create table if not exists temp_news
(
    source text,
    title text,
    link text,
    img_link text,
    description text,
    pub_date text
);
'''
create_users_table_q = '''
create table if not exists users
(
    id integer primary key,
    username text,
    first_name text,
    last_name text,
    rated integer default 0,
    is_new integer default 1,
    is_admin integer default 0,
    notify integer default 1
);
'''
create_suggested_news_table_q = '''
create table if not exists suggested_news (
    user_id integer,
    news_id integer,
    timestamp text,
    score  integer default -1,
    seen integer default 0
);
'''


class Database:

    def __init__(self, path):
        self.path = path
        # create all tables if not exists
        self.insert_query(create_news_table_q)
        self.insert_query(create_temp_news_table_q)
        self.insert_query(create_users_table_q)
        self.insert_query(create_suggested_news_table_q)

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
        # print(q)
        connection = self.connection
        return pd.read_sql_query(q, connection)

    def insert_query(self, q):
        # print(q)
        connection = self.connection
        cur = connection.cursor()
        cur.execute(q)
        connection.commit()
        connection.close()


    def is_notify(self, user_id):
        is_notify_df = self.select_query(f'select * from users where id = {user_id} and notify = 1')
        return not is_notify_df.empty

    def is_exist(self, user_id):
        is_exist_df = self.select_query(f'select * from users where id = {user_id}')
        return not is_exist_df.empty

    def is_admin(self, user_id):
        is_admin_df = self.select_query(f'select * from users where id = {user_id} and is_admin = 1')
        return not is_admin_df.empty

    def is_scored(self, user_id, news_id):
        if_scored_df = self.select_query(f'select * from suggested_news where news_id = {news_id} and user_id = {user_id} and score = -1')
        return if_scored_df.empty

    def set_notify(self, user_id, notify):
        self.insert_query(f'update users set notify = {notify} where id = {user_id}')

    def set_all_news_seen(self):
        self.insert_query(f'update suggested_news set seen = 1')

    def to_admin(self, user_id):
        self.insert_query(f'update users set is_admin = 1 where id = {user_id}')

    def from_admin(self, user_id):
        self.insert_query(f'update users set is_admin = 0 where id = {user_id}')

    def add_user(self, user_id, username, first_name, last_name):
        self.insert_query(f"insert into users (id, username, first_name, last_name) values ('{user_id}', '{username}', '{first_name}', '{last_name}')")

    def get_users(self):
        return self.select_query('select id from users')

    def get_news(self, news_id):
        return self.select_query(f'select * from news where id = {news_id}').iloc[0]
    
    def suggest_news(self, user_id, news_id):
        self.insert_query(f"insert into suggested_news (user_id, news_id, timestamp) values ({user_id}, {news_id}, datetime('now'))")

    def get_fresh_news_for_user(self, user_id):
        return self.select_query(f'''
            select * from news
            where
            (news.id not in (select news_id from suggested_news where user_id = {user_id}))
            and
            is_new = 1
        ''')


    def update_score(self, user_id, news_id, score):
        if not self.is_scored(user_id, news_id):
            self.insert_query(f'update users set rated = rated + 1 where id = {user_id}')
            self.insert_query(f'update suggested_news set score = {score} where news_id = {news_id} and user_id = {user_id}')

    def get_fresh_news(self, user_id):
        news_for_user_q = f'select news_id from suggested_news  where user_id = {user_id} and seen = 0 order by timestamp desc limit 1'
        news_for_user = self.select_query(news_for_user_q)
        if not news_for_user.empty:
            news_id = news_for_user.iloc[0][0]
            get_news_q = f'select id, title, description, link, img_link from news where id = {news_id}'
            news_data = self.select_query(get_news_q)
            if not news_data.empty:
                news_data = news_data.iloc[0]
                self.insert_query(f"update suggested_news set seen = 1 where user_id = {user_id} and news_id = {news_data['id']}")
                return news_data
        return pd.Series()


# 182301431