#!/usr/bin/env python3

import random
from base64 import b85decode
from string import ascii_letters, digits

from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest
from cipher.crypter import Crypter
from api import Api

ALPHA = ascii_letters + digits

checker = Checker()

@checker.define_check
def check(request: CheckRequest) -> Verdict:
    api = Api(request.hostname)
    res, err = ping(api)
    if err: return err

    res, err = register(api)
    if err: return err

    login, password, card, _, cookie = res
    res, err = get_cookie(api, login, password)
    if err: return err
    if res != cookie:
        return Verdict.MUMBLE("Wrong cookie")

    users, err = list_users(api)
    if err: return err
    if login not in users:
        return Verdict.MUMBLE("User not in users")

    res, err = check_card(api, login, card)
    if err: return err
    if res != card:
        return Verdict.MUMBLE("Wrong credit card")

    return Verdict.OK()

@checker.define_put(vuln_num=1, vuln_rate=1)
def put_1(request: PutRequest) -> Verdict:
    flag = request.flag
    api = Api(request.hostname)

    res, err = register(api)
    if err: return err
    login1, password1, card1, priv_key1, cookie1 = res

    res, err = register(api)
    if err: return err
    login2, password2, card2, priv_key2, cookie2 = res

    try:
        crypter = Crypter.load_private(b85decode(priv_key2.encode()))
    except Exception as ex:
        return Verdict.MUMBLE("Can't load private key")

    amount = random.randint(1, 100)
    description = crypter.encrypt(flag.encode())

    res, err = send_money(api, cookie2, login1, amount, description.hex())
    if err: return err

    users, err = list_users(api)
    if err: return err
    if login1 not in users or login2 not in users:
        return Verdict.MUMBLE("No user in users")

    flag_id = f'{login1}:{password1}:{priv_key1}:{cookie1}'
    return Verdict.OK(flag_id)

@checker.define_get(vuln_num=1)
def get_1(request: GetRequest) -> Verdict:
    login, password, priv_key, cookie = request.flag_id.strip().split(':')
    api = Api(request.hostname)

    res, err = get_cookie(api, login, password)
    if err: return err
    if res != cookie:
        return Verdict.MUMBLE("Wrong cookie")

    try:
        crypter = Crypter.load_private(b85decode(priv_key.encode()))
    except Exception as ex:
        print(ex)
        return Verdict.MUMBLE("Can't load private key")

    res, err = get_user(api, login)
    if err: return err
    _login, _balance, _pub_key = res

    if b85decode(_pub_key) != crypter.dump_public():
        return Verdict.MUMBLE("Wronf public key")

    transactions, err = get_transactions(api, login)
    if err: return err
    descriptions = []
    for transaction in transactions:
        description = bytes.fromhex(transaction['description'])
        descriptions.append(crypter.decrypt(description))

    if request.flag.encode() not in descriptions:
        return Verdict.CORRUPT("Wrong transaction's description")

    return Verdict.OK()

@checker.define_put(vuln_num=2, vuln_rate=1)
def put_2(request: PutRequest) -> Verdict:
    flag = request.flag
    api = Api(request.hostname)

    res, err = register(api, card=flag)
    if err: return err
    login, password, card, _, cookie = res

    res, err = get_user(api, login)
    if err: return err
    _login, _balance, _ = res
    if _login != login or _balance != 100:
        return Verdict.MUMBLE("Wrong user")

    flag_id = f'{login}:{password}:{cookie}'
    return Verdict.OK(flag_id)

@checker.define_get(vuln_num=2)
def get_2(request: GetRequest) -> Verdict:
    login, password, cookie = request.flag_id.strip().split(':')
    card = request.flag

    api = Api(request.hostname)

    users, err = list_users(api)
    if err: return err
    if login not in users:
        return Verdict.MUMBLE("No user in users")

    res, err = get_cookie(api, login, password)
    if err: return err
    if res != cookie:
        return Verdict.MUMBLE("Wrong cookie")

    card_pattern = card[:5] + ('_'*(len(card) - 11) + card[-6:])
    res, err = check_card(api, login, card_pattern)
    if err: return err
    if res != card:
        return Verdict.MUMBLE("Wrong credit card")

    return Verdict.OK()


def ping(api):
    result = api.ping()
    if result is None:
        return None, Verdict.DOWN("Can't ping service")
    if result["status"] != 200:
        return None, Verdict.MUMBLE("Wrong ping status")
    return "OK", None

def register(api, card=None):
    login = get_random_string(15)
    password = get_random_string(15)
    card = card or get_random_string(32)

    result = api.register(login, password, card)
    if result is None:
        return None, Verdict.DOWN("Can't register")

    if result['status'] != 200:
        return None, Verdict.MUMBLE("Wrong register status")

    if "addition" not in result or "priv_key" not in result["addition"] or "cookie" not in result["addition"]:
        return None, Verdict.MUMBLE("Wrong register data")

    priv_key = result["addition"]["priv_key"]
    cookie = result["addition"]["cookie"]

    return (login, password, card, priv_key, cookie), None


def send_money(api, cookie, login_to, amount, description):
    result = api.send_money(cookie, login_to, amount, description)
    if result is None:
        return None, Verdict.DOWN("Can't send money")

    if result['status'] != 200:
        return None, Verdict.MUMBLE("Wrong send money status")

    return 'OK', None

def get_cookie(api, login, password):
    result = api.get_cookie(login, password)
    if result is None:
        return None, Verdict.DOWN("Can't get cookie")

    if result['status'] != 200:
        return None, Verdict.MUMBLE("Wrong cookie status")

    if "addition" not in result or "cookie" not in result["addition"]:
        return None, Verdict.MUMBLE("Wrong cookie data")

    cookie = result["addition"]["cookie"]
    return cookie, None

def get_user(api, login):
    result = api.get_user(login)
    if result is None:
        return None, Verdict.DOWN("Can't get user")

    if result['status'] != 200:
        return None, Verdict.MUMBLE("Wrong get user status")

    if "addition" not in result or "pub_key" not in result["addition"] or "login" not in result["addition"] or "balance" not in result["addition"]:
        return None, Verdict.MUMBLE("Wrong user data")

    login = result["addition"]["login"]
    balance = result["addition"]["balance"]
    pub_key = result["addition"]["pub_key"]
    return (login, balance, pub_key), None

def get_transactions(api, login):
    result = api.get_transacions(login)
    if result is None:
        return None, Verdict.DOWN("Can't get transactions")

    if result['status'] != 200:
        return None, Verdict.MUMBLE("Wrong get tranaction status")

    if "addition" not in result or "transactions" not in result["addition"]:
        return None, Verdict.MUMBLE("Wrong transactions data")

    transactions = result["addition"]["transactions"]
    return transactions, None

def list_users(api):
    result = api.list_users()
    if result is None:
        return None, Verdict.DOWN("Can't list users")

    if result['status'] != 200:
        return None, Verdict.MUMBLE("Wrong list users status")

    if "addition" not in result or "users" not in result["addition"]:
        return None, Verdict.MUMBLE("Wrong list users data")

    users = result["addition"]["users"]
    return users, None

def check_card(api, login, credit_card):
    result = api.check_card(login, credit_card)
    if result is None:
        return None, Verdict.DOWN("Can't check card")

    if result['status'] != 200:
        return None, Verdict.MUMBLE("Wrong check card status")

    if "addition" not in result or "credit_card_credentials" not in result["addition"]:
        return None, Verdict.MUMBLE("Wrong check card data")

    credit_card_credentials = result["addition"]["credit_card_credentials"]
    return credit_card_credentials, None


def get_random_string(length):
    return ''.join(random.choice(ALPHA) for i in range(length))


checker.run()