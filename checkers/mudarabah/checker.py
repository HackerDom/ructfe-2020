#!/usr/bin/env python3.7

import client as c
import random
from string import ascii_letters, digits

from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest
from cipher.crypter import Crypter

ALPHA = ascii_letters + digits

checker = Checker()

@checker.define_check
def check(request: CheckRequest) -> Verdict:
    try:
        result = c.ping(request.hostname)
        if result and result['result'] and result['status'] == 200:
            return Verdict.OK()
        else:
            return Verdict.MUMBLE("Wrong ping answer")
    except Exception:
        return Verdict.DOWN("Servise down")

def check_service(request: CheckRequest) -> Verdict:
    login1 = get_random_string(10)
    password1 = get_random_string(10)
    card1 = get_random_string(10)

    login2 = get_random_string(10)
    print(login2)
    password2 = get_random_string(10)
    card2 = get_random_string(10)

    try:
        data = c.register(request.hostname, login1, password1, card1)
        cookie1, priv_key1 = data['cookie'], bytes.fromhex(data['priv_key'])

        data = c.register(request.hostname, login2, password2, card2)
        cookie2, priv_key2 = data['cookie'], bytes.fromhex(data['priv_key'])
    except Exception:
        return Verdict.MUMBLE("Can't register")

    crypter = Crypter.load_private(priv_key1)
    amount = random.randint(1, 90)
    flag = get_random_string(10).encode()
    descr = crypter.encrypt(flag)
    print(c.send_money(request.hostname, cookie1, login2, amount, descr.hex()))
    print(c.get_transactions(request.hostname, login2))

    return Verdict.OK()


def get_random_string(length):
    return ''.join(random.choice(ALPHA) for i in range(length))

checker.run()