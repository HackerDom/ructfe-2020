#!/usr/bin/env python3
import string
import random

from gornilo import Checker, CheckRequest, PutRequest, GetRequest, Verdict
import gornilo
from api import Api
import proto.office_pb2 as pb
import json
import re

checker = Checker()


def get_random_str(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def create_doc():
    return """
vars:
  b: 'bio'
exprs:
  - name: "bio"
    expr: "get_info(b)"
---
Hi '{username}'!
Bio: '{bio}'"""


def create_doc_with_flag(flag: str):
    return f"""
vars:
  sercretinfo: '{flag}'
---
Secret info: '{{sercretinfo}}'!!!"""


@checker.define_check
async def check_service(request: CheckRequest) -> Verdict:
    api = Api(f'{request.hostname}:8080')
    req = pb.ListDocumentsRequest()
    req.offset = 0
    req.limit = 100
    r, err = api.list_doc(req)
    if err != None:
        print(err)
        return Verdict.MUMBLE("failed to get response from service")
    req = pb.ListRequest()
    req.offset = 0
    req.limit = 100
    r, err = api.list_users(req)
    if err != None:
        print(err)
        return Verdict.MUMBLE("failed to get response from service")
    return Verdict.OK()


@checker.define_put(vuln_num=1, vuln_rate=2)
async def put(request: PutRequest) -> Verdict:
    api = Api(f'{request.hostname}:8080')
    name = get_random_str()
    password = get_random_str(30)
    req = pb.RegisterRequest()
    req.name = name
    req.password = password
    req.bio = request.flag
    r, err = api.register(req)
    if err != None:
        print(err)
        return Verdict.MUMBLE("failed to get response from service")

    req = pb.CreateDocumentRequest()
    req.name = get_random_str()
    req.doc = create_doc()
    r, err = api.create_doc(req)
    if err != None:
        print(err)
        return Verdict.MUMBLE("failed to get response from service")
    try:
        user_id = r.id
    except:
        return Verdict.MUMBLE("failed to get response from service")
    return Verdict.OK(f"{name}:{password}:{user_id}")


@checker.define_put(vuln_num=2, vuln_rate=1)
async def put_2(request: PutRequest) -> Verdict:
    api = Api(f'{request.hostname}:8080')
    name = get_random_str()
    password = get_random_str(30)
    req = pb.RegisterRequest()
    req.name = name
    req.password = password
    req.bio = request.flag
    r, err = api.register(req)
    if err != None:
        print(err)
        return Verdict.MUMBLE("failed to get response from service")
    req = pb.CreateDocumentRequest()
    req.name = name
    req.doc = create_doc_with_flag(request.flag)
    r, err = api.create_doc(req)
    if err != None:
        print(err)
        return Verdict.MUMBLE("failed to get response from service")
    try:
        user_id = r.id
    except:
        return Verdict.MUMBLE("failed to get response from service")
    return Verdict.OK(f"{name}:{password}:{user_id}")


@checker.define_get(vuln_num=1)
async def get(request: GetRequest) -> Verdict:
    api = Api(f'{request.hostname}:8080')
    name, password, id = request.flag_id.split(":")
    req = pb.ExecuteRequest()
    req.doc_id = int(id)
    req.username = name
    r, err = api.execute_doc(req)
    if err != None:
        print(err)
        return Verdict.MUMBLE("failed to get response from service")
    try:
        executed = r.executed
    except:
        err = "invalid resp format"
        return Verdict.MUMBLE(err)

    di, err = DocInfo.parse(executed)
    if err != None:
        return Verdict.MUMBLE(err)
    if di.bio != request.flag:
        return Verdict.MUMBLE("invalid flag")
    return Verdict.OK()


@checker.define_get(vuln_num=2)
async def get_2(request: GetRequest) -> Verdict:
    api = Api(f'{request.hostname}:8080')
    name, password, id = request.flag_id.split(":")
    req = pb.ExecuteRequest()
    req.doc_id = int(id)
    req.username = name
    r, err = api.execute_doc(req)
    if err != None:
        print(err)
        return Verdict.MUMBLE("failed to get response from service")
    try:
        executed = r.executed
    except:
        err = "invalid resp format"
        return Verdict.MUMBLE(err)
    di, err = DocInfo.parse_static(executed)
    if err != None:
        return Verdict.MUMBLE(err)
    if di.secret_info != request.flag:
        return Verdict.MUMBLE("invalid flag")
    return Verdict.OK()


class DocInfo:
    USERNAME_RE = "Hi '(.*)'!"
    BIO_RE = "Bio: '(.*)'"
    SECRET_RE = "Secret info: '(.*)'!!!"

    def __init__(self, username: str, bio: str, secret_info: str):
        self.username: str = username
        self.bio: str = bio
        self.secret_info: str = secret_info

    @staticmethod
    def parse(content: str) -> (object, str):
        splitted = content.split('\n')
        if len(splitted) != 2:
            print(f"invalid lines count was: {len(splitted)} want: 2")
            return None, "invalid doc format"
        try:
            m = re.match(DocInfo.USERNAME_RE, splitted[0])
            username = m.group(1)
            m = re.search(DocInfo.BIO_RE, splitted[1])
            bio = m.group(1)
        except Exception as e:
            print(e)
            return None, "invalid doc format"
        return DocInfo(username, bio, ""), None

    @staticmethod
    def parse_static(content: str) -> (object, str):
        splitted = content.split('\n')
        if len(splitted) != 1:
            print(f"invalid lines count was: {len(splitted)} want: 1")
            return None, "invalid doc format"
        try:
            m = re.match(DocInfo.SECRET_RE, splitted[0])
            secret_info = m.group(1)
        except Exception as e:
            print(e)
            return None, "invalid doc format"
        return DocInfo("", "", secret_info), None


if __name__ == '__main__':
    checker.run()
