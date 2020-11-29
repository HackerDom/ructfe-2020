import psycopg2
from psycopg2 import sql
from hashlib import md5
import user_model
from crypter import Crypter

conn = None

def connect_to_db():
    global conn
    conn = psycopg2.connect(dbname='postgres', user='postgres',
                                     password='postgres', host='postgres')

def check_and_refresh_connect():
    global conn
    try:
        conn.isolation_level
    except psycopg2.OperationalError:
        connect_to_db()

class DatabaseClient:
    def __init__(self):
        pass
    
    def __enter__(self):
        check_and_refresh_connect()
        global conn
        self.conn = conn  
        self.cursor = conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def check_user(self, user):
        self.cursor.execute('select * from public.users where login = %s', (user.login, ))
        u = self.cursor.fetchone()
        print(f"user {u}, hash: {user.password_hash}")
        if u is None or u[1] != user.password_hash:
            return False
        else:
            return True
    
    def check_if_username_free(self, username):
        self.cursor.execute('select * from public.users where login = %s', (username, ))
        u = self.cursor.fetchone()
        print(f"user in check_username {u}", flush=True)
        if u is None:
            return True
        else:
            return False
        
    def add_user(self, user):
        self.cursor.execute("INSERT INTO public.users (login, password_hash, public_key, credit_card_credentials, balance, cookie) VALUES(%s, %s, %s, %s, %s, %s)", (user.login, user.password_hash, user.public_key_base64, user.credit_card_credentials, user.balance, user.cookie))
        self.conn.commit()

    def get_all_users_all_info(self):
        self.cursor.execute('select * from public.users')
        u = self.cursor.fetchall()
        return u
    
    def get_all_users(self):
        self.cursor.execute('select (login, public_key) from public.users')
        u = self.cursor.fetchall()
        return u

    def select_user_by_login_and_pass(self, username, password):
        print("in select user", flush=True)
        password_hash = md5(password.encode('utf-8')).hexdigest()
        print(username, password_hash, flush=True)
        self.cursor.execute('select * from public.users where login=%s AND password_hash=%s', (username, password_hash))
        u = self.cursor.fetchone()
        print(f"user in select_user {u}", flush=True)
        if u:
            return user_model.User(*(u[1:])) # strange notation because of timeshtamp
        return None
    
    def select_user_by_login(self, username):
        print("in select user without password", flush=True)
        print(username, flush=True)
        self.cursor.execute('select * from public.users where login=%s', (username, ))
        u = self.cursor.fetchone()
        print(f"user in select_user_without_password {u}", flush=True)
        if u:
            return user_model.User(*(u[1:])) # strange notation because of timeshtamp
        return None
    
    def select_user_by_cookie(self, cookie):
        print("in select user by cookie", flush=True)
        print(cookie, flush=True)
        self.cursor.execute('select * from public.users where cookie=%s', (cookie, ))
        u = self.cursor.fetchone()
        print(f"user in select_user_by_cookie {u}", flush=True)
        if u:
            return user_model.User(*(u[1:])) # strange notation because of timeshtamp
        return None
    
    def get_all_transactions(self):
        self.cursor.execute('select * from transactions')
        u = self.cursor.fetchall()
        return u
    
    def add_transaction(self, transaction):
        c = Crypter()
        data = transaction.dumps()
        encrypted_data = c.encrypt(data)
        self.cursor.execute("INSERT INTO public.transactions (login_from, encrypted_data) VALUES(%s, %s)", (transaction.login_from, encrypted_data))
        self.conn.commit()

