#!/usr/bin/env python3
import base64
import hashlib
import sys

import requests
import traceback
import random
import string

from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest


checker = Checker()


PORT = 3687


REGISTER_URL = "http://{hostname}:{port}/register"
LOGIN_URL = "http://{hostname}:{port}/login"
FILE_URL = "http://{hostname}:{port}/files/{filename}"
INDEX_URL = "http://{hostname}:{port}/"

ALPHA = string.ascii_letters + string.digits


def gen_string():
    return ''.join(random.choice(ALPHA) for _ in range(20))


def register(hostname, username, password):
    session = requests.Session()
    files = {'login': (None, username), 'password': (None, password)}
    url = REGISTER_URL.format(hostname=hostname, port=PORT)
    r = session.post(url, files=files)
    r.raise_for_status()
    return session


def login(hostname, username, password):
    session = requests.Session()
    files = {'login': (None, username), 'password': (None, password)}
    url = LOGIN_URL.format(hostname=hostname, port=PORT)
    r = session.post(url, files=files)
    r.raise_for_status()
    return session


def upload_file(session, hostname, filename, content):
    url = FILE_URL.format(hostname=hostname, port=PORT, filename=filename)
    r = session.post(url, files={"file": ("file", content, "text")})
    r.raise_for_status()


def download_file(session, hostname, filename):
    url = FILE_URL.format(hostname=hostname, port=PORT, filename=filename)
    r = session.get(url)
    r.raise_for_status()
    return r.content.decode()


class NetworkChecker:
    def __init__(self):
        self.verdict = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type in {requests.exceptions.ConnectionError, ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError}:
            self.verdict = Verdict.DOWN("Service is down")
        if exc_type in {requests.exceptions.HTTPError}:
            self.verdict = Verdict.MUMBLE(f"Incorrect http code")

        if exc_type:
            print(exc_type)
            print(exc_value.__dict__)
            traceback.print_tb(exc_traceback, file=sys.stdout)
        return True


@checker.define_check
def check_service(request: CheckRequest) -> Verdict:
    with NetworkChecker() as nc:
        r = requests.get(INDEX_URL.format(hostname=request.hostname, port=PORT))
        r.raise_for_status()
    return nc.verdict


@checker.define_put(vuln_num=1, vuln_rate=1)
def put_flag(request: PutRequest) -> Verdict:
    with NetworkChecker() as nc:
        username, password, filename = gen_string(), gen_string(), gen_string()
        flag_id = f"{username}:{password}:{filename}"
        session = register(request.hostname, username, password)
        upload_file(session, request.hostname, filename, request.flag)
        nc.verdict = Verdict.OK(flag_id)
    return nc.verdict


@checker.define_get(vuln_num=1)
def get_flag(request: GetRequest) -> Verdict:
    with NetworkChecker() as nc:
        username, password, filename = request.flag_id.strip().split(":")
        session = login(request.hostname, username, password)
        real_flag = download_file(session, request.hostname, filename)
        if request.flag != real_flag:
            print(f"Different flags, expected: {request.flag}, real: {real_flag}")
            return Verdict.CORRUPT("Corrupt flag")
        nc.verdict = Verdict.OK()
    return nc.verdict


def get_hash(text: str) -> str:
    return base64.b64encode(hashlib.md5(text.encode()).digest()).decode()


if __name__ == '__main__':
    checker.run()
