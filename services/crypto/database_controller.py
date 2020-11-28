import psycopg2
from psycopg2 import sql
from hashlib import md5
import user_model

class DatabaseClient:
    def __init__(self):
        pass

    def __enter__(self):
        self.conn = psycopg2.connect(dbname='postgres', user='postgres',
                                     password='postgres', host='postgres')
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.conn.close()
    
    def check_user(self, user):
        self.cursor.execute('select * from users where login = %s', (user.login, ))
        u = self.cursor.fetchone()
        print(f"user {u}, hash: {user.password_hash}")
        if u is None or u[1] != user.password_hash:
            return False
        else:
            return True
    
    def check_username(self, username):
        self.cursor.execute('select * from users where login = %s', (username, ))
        u = self.cursor.fetchone()
        print(f"user in check_username {u}", flush=True)
        if u is None:
            return True
        else:
            return False
        
    def add_user(self, user):
        if not self.check_username(user.login):
            raise ValueError
        self.cursor.execute("INSERT INTO users (login, password_hash, public_key, credit_card_credentials) VALUES(%s, %s, %s, %s)", (user.login, user.password_hash, user.public_key_base64, user.credit_card_credentials))
        self.conn.commit()

    def get_all_users_all_info(self):
        self.cursor.execute('select * from users')
        u = self.cursor.fetchall()
        return u
    
    def get_all_users(self):
        self.cursor.execute('select (login, public_key) from users')
        u = self.cursor.fetchall()
        return u

    def select_user(self, username, password):
        print("in select user", flush=True)
        password_hash = md5(password.encode('utf-8')).hexdigest()
        print(username, password_hash, flush=True)
        self.cursor.execute('select * from users where login=%s AND password_hash=%s', (username, password_hash))
        u = self.cursor.fetchone()
        print(f"user in select_user {u}", flush=True)
        if u:
            return user_model.User(u[0], u[1], u[2], u[3])
        return None