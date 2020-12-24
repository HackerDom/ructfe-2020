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
    crypter = Crypter.load_private(priv_key)
    new_conditions = {"addition": {"cookie":token, "login_to":login_to, "amount":int(amount), "description":crypter.encrypt(description.encode()).hex()}}
    req = urllib.request.Request(HOST+"/send_money",
                                    data=json.dumps(new_conditions).encode('utf-8'),
                                    headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))

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
        res = register(args.login, args.password, args.credit_card_credentials)
        priv_key_hex = res["priv_key"]
        with open(f"{args.login}.key", "wb") as f:
            f.write(bytes.fromhex(priv_key_hex))
            print(f"key is written to {args.login}.key")
        print(res)
    if args.get_cookie:
        print(get_token(args.login, args.password))
    if args.send_money:
        if args.priv_key_filename:
            with open(args.priv_key_filename, "rb") as f:
                key = f.read()
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