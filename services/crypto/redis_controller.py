import redis
import os

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", "6379")

r = redis.StrictRedis(host=redis_host, 
    port=redis_port, db=0)

def username_in_db(username):
    return f"user:{username}".encode('utf-8')

def cookie_in_db(cookie):
    return f"cookie:{cookie}".encode('utf-8')

def add_to_store(username, cookie):
    print("set: ", cookie_in_db(cookie), username_in_db(username), flush=True)
    r.set(cookie_in_db(cookie), username_in_db(username))

def check_username_by_cookie(username, cookie):
    if get_username_by_cookie(cookie)== username_in_db(username):
        return True
    return False

def get_username_by_cookie(cookie):
    print("get: ", cookie, flush=True)
    return r.get(cookie_in_db(cookie)).decode('utf-8').split(':')[1]