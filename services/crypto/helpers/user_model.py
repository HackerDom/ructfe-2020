from hashlib import md5
import re
from helpers.helpers import *

class User:
    def __init__(self, login, password, public_key_base64, credit_card_credentials, balance, cookie):
        self.login = login
        self.password_hash = md5(password.encode('utf-8')).hexdigest()
        self.cookie = cookie
        self.public_key_base64 = public_key_base64
        self.credit_card_credentials = credit_card_credentials
        self.balance = balance
    
    def __repr__(self):
        return f"login {self.login} pubkey {self.public_key_base64}"

    def __str__(self):
        return f"login {self.login} pubkey {self.public_key_base64}"

def create_new(login, password, public_key_base64, credit_card_credentials):
    cookie = create_cookie(login, password)
    default_balace = 100
    return User(login, password, public_key_base64, credit_card_credentials, default_balace, cookie)