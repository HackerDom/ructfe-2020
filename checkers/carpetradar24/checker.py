import client as c
import random
import string

from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest

checker = Checker()


@checker.define_check
def check_service(request: CheckRequest) -> Verdict:
    login1 = get_random_string(10)
    password1 = get_random_string(10)
    login2 = get_random_string(10)
    password2 = get_random_string(10)
    try:
        check_register(login1, password1)
        check_register(login2, password2)
    except Exception:
        return Verdict.MUMBLE("Can't register")
    try:
        token_from = c.get_token(login1, password1)
        token_to = c.get_token(login2, password2)
    except Exception:
        return Verdict.MUMBLE("Can't get token")
    try:
        amount = random.randint(1, 90)
        descr = get_random_string(10)
        check_money_sending(token_from, token_to, amount, descr)
    except Exception:
        return Verdict.MUMBLE("Can't send money")
    return Verdict.OK()


def check_register(login, password):
    credit_card_credentials = get_random_string(10)
    pubkey = get_random_string(10)  # change after crypto implementation
    c.register(login, password, credit_card_credentials, pubkey)
    user = c.get_user_by_login_and_password(login, password)
    if not (user["login"] == login and
            user["credit_card_credentials"] == credit_card_credentials and
            user["public_key_base64"] == pubkey):
        raise ValueError


def check_money_sending(token_from, token_to, amount, description):
    from_before = int(c.get_user_by_token(token_from)["balance"])
    to_before = int(c.get_user_by_token(token_to)["balance"])
    to = c.get_user_by_token(token_to)["login"]
    c.send_money(token_from, to, amount, description)
    from_after = int(c.get_user_by_token(token_from)["balance"])
    to_after = int(c.get_user_by_token(token_to)["balance"])
    if not (from_before - amount == from_after and
            to_before + amount == to_after):
        raise ValueError


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

