#!/usr/bin/env python3

import requests
import socket
import random
import time
import uuid
import string

from gornilo import \
    GetRequest, \
    CheckRequest, \
    PutRequest, \
    Checker, \
    Verdict


checker = Checker()

UDP_PORT = 7125
TCP_PORT = 7124


def rand_string(n=32):
    return ''.join(
        random.SystemRandom()
            .choice(string.ascii_uppercase + string.digits)
        for _ in range(n))


@checker.define_check
def check(check_request: CheckRequest) -> Verdict:
    data_check = uuid.uuid4()
    rand_data = rand_string(random.randint(20, 40))

    try:
        for i in range(random.randint(1, 4)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
            sock.sendto(bytes(f"{data_check}:{rand_data}", "utf-8"), (check_request.hostname, UDP_PORT))
            time.sleep(random.randint(1, 4) * 0.1)
    except Exception as e:
        print(e)
        return Verdict.DOWN("can't send u anything")

    try:
        resp = requests.get(
            f"http://{check_request.hostname}:{TCP_PORT}/data/{data_check}")
        if resp.content.decode().strip("\x00") == rand_data:
            return Verdict.OK()
        else:
            return Verdict.CORRUPT("u re sending corrupt data")
    except Exception as e:
        print(e)
        return Verdict.MUMBLE("service mubmbles too hard")


@checker.define_put(vuln_num=1, vuln_rate=1)
def put(put_request: PutRequest) -> Verdict:
    data_check = str(uuid.uuid4())
    rand_data = put_request.flag

    try:
        for i in range(random.randint(1, 4)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
            sock.sendto(bytes(f"{data_check}:{rand_data}", "utf-8"), (put_request.hostname, UDP_PORT))
            time.sleep(random.randint(1, 4) * 0.1)
        return Verdict.OK(data_check)
    except Exception as e:
        print(e)
        return Verdict.DOWN("can't send u anything")


@checker.define_get(vuln_num=1)
def get(get_request: GetRequest) -> Verdict:
    try:
        resp = requests.get(
            f"http://{get_request.hostname}:{TCP_PORT}/data/{get_request.flag_id.strip()}")
        if resp.content.decode().strip("\x00") == get_request.flag:
            return Verdict.OK()
        else:
            return Verdict.CORRUPT("u re sending corrupt data")
    except Exception as e:
        print(e)
        return Verdict.MUMBLE("service mubmbles too hard")


if __name__ == "__main__":
    checker.run()