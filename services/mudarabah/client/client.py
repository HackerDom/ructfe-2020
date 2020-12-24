import json
import urllib.request
from arg_parse import get_parsed_args
from cipher.crypter import Crypter

HOST = "http://localhost:3113"


def get_token(login, password):
    new_conditions = {"addition": {"login": login, "password":password}}
    req = urllib.request.Request(HOST+"/get_cookie", data=json.dumps(new_conditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]["cookie"]


def register(login, password, credit_card_credentials):
    new_conditions = {"addition": {"login": login, "password":password, "credit_card_credentials":credit_card_credentials}}
    req = urllib.request.Request(HOST+"/register", data=json.dumps(new_conditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def send_money(token, login_to, amount, description, priv_key):
    crypter = Crypter.load_private(bytes.fromhex(priv_key))
    new_conditions = {"addition": {"cookie":token, "login_to":login_to, "amount":amount, "description":crypter.encrypt(description.encode())}}
    req = urllib.request.Request(HOST+"/send_money",
                                    data=json.dumps(new_conditions).encode('utf-8'),
                                    headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_users():
    req = urllib.request.Request(HOST+"/users_pubkeys", 
                                headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_transaction(login):
    new_conditions = {"addition": {"login": login}}
    req = urllib.request.Request(HOST+"/transactions", data=json.dumps(new_conditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_user(login):
    new_conditions = {"addition": {"login": login}}
    req = urllib.request.Request(HOST+"/get_user", data=json.dumps(new_conditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_user_listing():
    req = urllib.request.Request(HOST+"/list_users",
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def main():
    args = get_parsed_args()
    if args.register:
        print(register(args.login, args.password, args.credit_card_credentials))
    if args.get_cookie:
        print(get_token(args.login, args.password))
    if args.send_money:
        #please check it
        if args.priv_key_filename:
            with open(args.priv_key_filename, "r") as f:
                key = f.read() # should be hex
        else:
            key = args.priv_key 
        print(send_money(args.cookie, args.login_to, args.amount, args.description, key))
    if args.get_transactions:
        print(get_transaction(args.login))
    if args.get_user:
        print(get_user(args.login))
    if args.get_user_listing:
        print(get_user_listing())

if __name__ == "__main__":
    main()