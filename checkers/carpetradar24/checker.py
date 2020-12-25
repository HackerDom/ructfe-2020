#!/usr/bin/env python3
import uuid
import client as c
import random
import string
from functools import wraps
from gornilo import Checker, Verdict, CheckRequest, PutRequest, GetRequest
import traceback
import requests

checker = Checker()

TCP_PORT = 12345
HTTP_PORT = 7000

code = {
    101: "OK",
    102: "CORRUPT",
    103: "MUMBLE",
    104: "DOWN",
    110: "CHECKER_ERROR"
}


def check_exception(func):
    @wraps(func)
    def inner(request, *args, **kwargs) -> Verdict:
        try:
            result = func(request, *args, **kwargs)
        except (ConnectionError, requests.exceptions.RequestException):
            traceback.print_exc()
            result = Verdict.DOWN("Connection error")
        except Exception:
            traceback.print_exc()
            print("Unknown error")
            result = Verdict.MUMBLE("Something went wrong")

        print(f"Return verdict: [{result._code} {code[result._code]}] <{result._public_message}>")
        return result

    return inner


@checker.define_check
@check_exception
def check_service(request: CheckRequest) -> Verdict:
    client = c.Client(request.hostname, TCP_PORT, HTTP_PORT)

    login, password = get_creds()
    company = get_random_string(15)
    token = client.register_and_get_auth_token(login, password, company)
    if token is None:
        return Verdict.MUMBLE("Can't register and get auth token")

    flight_id = uuid.uuid4()
    label = get_random_string(15)
    license = get_random_string(32)
    r = client.send_flight_state(token, get_random_int(), get_random_int(), flight_id.bytes, label, license, False)
    r = client.send_flight_state(token, get_random_int(), get_random_int(), flight_id.bytes, label, license, False)

    positions = client.get_main_page_positions()
    if positions is None:
        return Verdict.MUMBLE("Can't get or parse main page")

    if len(positions) == 0:
        print(f"[---] Positions list is empty")
        return Verdict.MUMBLE("Not enough rows in positions list")
    print(f"[+] Positions list has {len(positions)} rows")

    try:
        emails = []
        for p in positions:
            if len(positions) == 0:
                return Verdict.MUMBLE("Not enough values in position row")
            emails.append(p[-1])
    except Exception:
        print(f"[---] Failed to extract emails from positions list")
        traceback.print_exc()
        return Verdict.MUMBLE("Incorrect positions list")

    if f"{login}@carpetradar24.ru" not in emails:
        print("[---] Not found login on main page")
        return Verdict.MUMBLE("Service returned incorrect main page")

    print("[+] Found my login on main page")
    return Verdict.OK()


@checker.define_put(vuln_num=1, vuln_rate=1)
@check_exception
def put_flag(request: PutRequest) -> Verdict:
    client = c.Client(request.hostname, TCP_PORT, HTTP_PORT)

    login, password = get_creds()
    company = get_random_string(15)
    token = client.register_and_get_auth_token(login, password, company)
    if token is None:
        return Verdict.MUMBLE("Can't register or parse auth token")

    print(f"[+] Registered, will try to send my position")
    flight_id = uuid.uuid4()
    label = get_random_string(15)
    license = request.flag
    response = client.send_flight_state(token, get_random_int(), get_random_int(), flight_id.bytes, label, license,
                                        False)

    return Verdict.OK(f"{login}:{password}")


@checker.define_get(vuln_num=1)
@check_exception
def get_flag(request: GetRequest) -> Verdict:
    client = c.Client(request.hostname, TCP_PORT, HTTP_PORT)

    login, password = request.flag_id.strip().split(":")
    token = client.login_and_get_auth_token(login, password)
    if token is None:
        print(f"[---] Cannot log in, maybe user data is lost")
        return Verdict.CORRUPT("Can't login or parse auth token")

    flights = client.get_chronicle(token)
    if flights is None:
        return Verdict.MUMBLE("Can't get or parse chronicle")

    if len(flights) < 1 or len(flights[0]) < 8:
        print(f"[---] Flights list length in chronicle is incorrect, maybe user flights data is lost")
        return Verdict.CORRUPT("Not enough records in chronicle")
    print(f"[+] Flights list has {len(flights)} rows")
    print(f"[+] Will compare expected and actual flags")

    if flights[0][1] != request.flag:
        print(f"Flag '{flights[0][1]}' not equal to expected '{request.flag}'. Creds: {login}:{password}")
        return Verdict.CORRUPT("Service returned incorrect flag")

    return Verdict.OK()


def get_random_string(k=10):
    return ''.join(random.choices(string.ascii_lowercase, k=k))


def get_creds():
    return get_random_string(), get_random_string()


def get_random_int():
    return random.randint(1, 1024 * 1024 * 1024)


if __name__ == '__main__':
    checker.run()
