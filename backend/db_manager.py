import sqlite3

# path = '../news.db'

class DB:

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
        return DB.connect_db(self.path)
    
    # def select_query(self, q):
    #     connection = DB.connect_db(self.path)
    #     connection.cursor.execute(q)
    #     return connection.cursor.fetchall()



