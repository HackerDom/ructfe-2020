#!/usr/bin/env python3

import random
from string import ascii_letters, digits

from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest
from cipher.crypter import Crypter
from api import Api

ALPHA = ascii_letters + digits

checker = Checker()

@checker.define_check
def check(request: CheckRequest) -> Verdict:
    api = Api(request.hostname)
    try:
        result = api.ping()
        if result and result['status'] == 200:
            return Verdict.OK()
        else:
            return Verdict.MUMBLE("Wrong ping status")
    except Exception as ex:
        print(ex)
        return Verdict.DOWN("Servise down")

@checker.define_put(vuln_num=1, vuln_rate=1)
def put(request: PutRequest) -> Verdict:
    flag = request.flag
    api = Api(request.hostname)

    res, err = register(api)
    if err: return err
    login1, password1, card1, priv_key1, cookie1 = res

    res, err = register(api)
    if err: return err
    login2, password2, card2, priv_key2, cookie2 = res

    try:
        crypter = Crypter.load_private(bytes.fromhex(priv_key2))
    except Exception as ex:
        print(ex)
        return Verdict.MUMBLE("Can't load private key")

    amount = random.randint(1, 100)
    description = crypter.encrypt(flag.encode())

    res, err = send_money(api, cookie2, login1, amount, description.hex())
    if err: return err

    flag_id = f'{login1}:{password1}:{priv_key1}:{cookie1}'
    return Verdict.OK(flag_id)

@checker.define_get(vuln_num=1)
def get(request: GetRequest) -> Verdict:
    api = Api(request.hostname)
    login, password, priv_key, cookie = request.flag_id.strip().split(':')

    res, err = get_cookie(api, login, password)
    if err: return err
    if res != cookie:
        return Verdict.MUMBLE("Wrong cookie")

    try:
        crypter = Crypter.load_private(bytes.fromhex(priv_key))
    except Exception as ex:
        print(ex)
        return Verdict.MUMBLE("Can't load private key")

    res, err = get_public_key(api, login)
    if err: return err
    if res != crypter.dump_public().hex():
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


def register(api):
    login = get_random_string(10)
    password = get_random_string(10)
    card = get_random_string(10)

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

    if "addition" not in result or "cookie" not in result["addition"]:
        return None, Verdict.MUMBLE("Wrong cookie data")

    cookie = result["addition"]["cookie"]
    return cookie, None

def get_public_key(api, login):
    result = api.get_public_key(login)
    if result is None:
        return None, Verdict.DOWN("Can't get public key")

    if "addition" not in result or "pub_key" not in result["addition"]:
        return None, Verdict.MUMBLE("Wrong public key data")

    pub_key = result["addition"]["pub_key"]
    return pub_key, None

def get_transactions(api, login):
    result = api.get_transacions(login)
    if result is None:
        return None, Verdict.DOWN("Can't get transactions")

    if "addition" not in result or "transactions" not in result["addition"]:
        return None, Verdict.MUMBLE("Wrong transactions data")

    transactions = result["addition"]["transactions"]
    return transactions, None


def get_random_string(length):
    return ''.join(random.choice(ALPHA) for i in range(length))


checker.run()