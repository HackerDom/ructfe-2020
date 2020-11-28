from hashlib import md5
import re
import redis_controller
username_pattern = re.compile(r"^[A-Za-z0-9]+$")

class User:
    def __init__(self, login, password, public_key_base64, credit_card_credentials):
        if self.check_username(login):
            self.login = login
        else:
            raise ValueError
        self.password_hash = md5(password.encode('utf-8')).hexdigest()
        self.cookie = md5(f"{login}{password}".encode('utf-8')).digest()
        self.public_key_base64 = public_key_base64
        self.credit_card_credentials = credit_card_credentials
        #redis_controller.add_to_store(self.login, self.cookie)

    def check_username(self, username):
        if username_pattern.match(username):
            return True
        else:
            return False
    
    def __repr__(self):
        return f"login {self.login} pubkey {self.public_key_base64}"

    def __str__(self):
        return f"login {self.login} pubkey {self.public_key_base64}"


def check_auth(session_user_cookie):
    try:
        if redis_controller.get_username_by_cookie(session_user_cookie) is not None:
            return True
        return False
    except KeyError:
        return False
    except AttributeError:
        return False