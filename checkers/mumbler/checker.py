#!/usr/bin/env python3
import requests
import socket
import random
import time
import uuid
import string
from traceback import print_exc
from user_agent_randomizer import get as get_user_agent
from requests.exceptions import Timeout
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from gornilo import \
    GetRequest, \
    CheckRequest, \
    PutRequest, \
    Checker, \
    Verdict


def requests_with_retry(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(400, 404, 500, 502),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    return session


checker = Checker()

UDP_PORT = 7125
TCP_PORT = 7124


def rand_string(n=32):
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(n))


@checker.define_check
def check(check_request: CheckRequest) -> Verdict:
    data_check = uuid.uuid4()
    rand_data = rand_string(random.randint(20, 40))
    rand_ports_range = random.randint(len(str(data_check) + rand_data) + 1, len(str(data_check) + rand_data) + 20)

    try:
        resp = requests_with_retry().get(
            f"http://{check_request.hostname}:{TCP_PORT}/open/{rand_ports_range}",
            headers={"User-Agent": get_user_agent()}
        )
        port = int(resp.content)

        for i in range(random.randint(1, 3)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
            sock.sendto(bytes(f"{data_check}:{rand_data}", "utf-8"), (check_request.hostname, port))
            time.sleep(random.randint(1, 4) * 0.1)
    except Exception as e:
        print(e, print_exc())
        return Verdict.DOWN("can't send u anything")

    try:
        resp = requests_with_retry().get(
            f"http://{check_request.hostname}:{TCP_PORT}/data/{data_check}",
            headers={"User-Agent": get_user_agent()},
            timeout=3
        )
        if resp.content.decode().strip("\x00") == rand_data:
            return Verdict.OK()
        else:
            return Verdict.CORRUPT("u re sending corrupt data")
    except Timeout as e:
        print(e, print_exc())
        return Verdict.DOWN("service seems not responding")
    except Exception as e:
        print(e, print_exc())
        return Verdict.MUMBLE("service mubmbles too hard")


@checker.define_put(vuln_num=1, vuln_rate=1)
def put(put_request: PutRequest) -> Verdict:
    data_check = str(uuid.uuid4())
    rand_data = put_request.flag
    rand_ports_range = random.randint(len(str(data_check) + rand_data) + 1, len(str(data_check) + rand_data) + 20)

    try:
        resp = requests_with_retry().get(
            f"http://{put_request.hostname}:{TCP_PORT}/open/{rand_ports_range}",
            headers={"User-Agent": get_user_agent()}
        )
        port = int(resp.content)

        for i in range(random.randint(1, 1)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
            sock.sendto(bytes(f"{data_check}:{rand_data}", "utf-8"), (put_request.hostname, port))
            time.sleep(random.randint(1, 4) * 0.1)
        return Verdict.OK(data_check)
    except Exception as e:
        print(e, print_exc())
        return Verdict.DOWN("can't send u anything")


@checker.define_get(vuln_num=1)
def get(get_request: GetRequest) -> Verdict:
    try:
        resp = requests_with_retry().get(
            f"http://{get_request.hostname}:{TCP_PORT}/data/{get_request.flag_id.strip()}",
            headers={"User-Agent": get_user_agent()},
            timeout=3
        )
        if resp.content.decode().strip("\x00") == get_request.flag:
            return Verdict.OK()
        else:
            return Verdict.CORRUPT("u re sending corrupt data")
    except Timeout as e:
        print(e, print_exc())
        return Verdict.DOWN("service seems not responding")
    except Exception as e:
        print(e, print_exc())
        return Verdict.CORRUPT("service can't give a flag")


if __name__ == "__main__":
    checker.run()