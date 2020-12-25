#!/usr/bin/env python3
import base64
import hashlib
import sys

import requests
import traceback
import random
import string


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


def process_file(session, hostname, filename):
    url = FILE_URL.format(hostname=hostname, port=PORT, filename=filename)
    r = session.get(url)
    r.raise_for_status()
    return r.content.decode()
