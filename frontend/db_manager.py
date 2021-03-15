import sqlite3
import pandas as pd

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




