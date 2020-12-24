#!/usr/bin/env python3
import random

from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest

from client import Client


def generate_username():
    return 'asdf' + str(random.randint(0, 2**32))


def generate_name():
    return 'Asdf Asdf'


def generate_phone():
    return '+12345'


def generate_title():
    return 'title'


def generate_text():
    return 'text'


checker = Checker()


@checker.define_check
def check_service(request: CheckRequest) -> Verdict:
    return Verdict.OK()


@checker.define_put(vuln_num=1, vuln_rate=1)
def put_flag(request: PutRequest) -> Verdict:
    client = Client(request.hostname)
    username = generate_username()
    name = generate_name()
    phone = generate_phone()
    password = client.register(username, name, phone, address=request.flag)
    title = generate_title()
    text = generate_text()
    doc_id = client.sign(title=title, text=text)
    return Verdict.OK(flag_id=f'{doc_id}:{title}:{username}:{password}')


@checker.define_get(vuln_num=1)
def get_flag(request: GetRequest) -> Verdict:
    client = Client(request.hostname)
    doc_id, title, username, password = request.flag_id.strip().split(':', 3)
    doc_id = int(doc_id)

    client.log_in(username, password)
    profile = client.profile()
    if request.flag.encode('utf-8') not in profile:
        return Verdict.CORRUPT('A flag is missing')

    doc = client.doc(doc_id)
    if title.encode('utf-8') not in doc:
        return Verdict.MUMBLE('A document disappeared')

    return Verdict.OK()


if __name__ == '__main__':
    checker.run()
