#!/usr/bin/python3
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


@checker.define_check
async def check_service(request: CheckRequest) -> Verdict:
    api = Api(f'{request.hostname}:8080')
    req = pb.ListDocumentsRequest()
    req.offset = 0
    req.limit = 100
    r = api.list_doc(req)
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

    req = pb.CreateDocumentRequest()
    req.name = get_random_str()
    req.doc = create_doc()
    r = api.create_doc(req)

    resp = json.loads(r.text)
    return Verdict.OK(f"{name}:{password}:{resp['id']}")


@checker.define_get(vuln_num=1)
async def get(request: GetRequest) -> Verdict:
    api = Api(f'{request.hostname}:8080')

    name, password, id = request.flag_id.split(":")
    req = pb.ExecuteRequest()

    req.doc_id = int(id)
    req.username = name
    r = api.execute_doc(req)
    try:
        print(r.text)
        executed = json.loads(r.text)['executed']
    except:
        err = "invalid resp format"
        return Verdict.MUMBLE(err)
    di, err = DocInfo.parse(executed)
    if err != None:
        return Verdict.MUMBLE(err)
    return Verdict.OK()


class DocInfo:
    USERNAME_RE = "Hi '(.*)'!"
    BIO_RE = "Bio: '(.*)'"

    def __init__(self, username: str, bio: str):
        self.username: str = username
        self.bio: str = bio

    @staticmethod
    def parse(content: str) -> (object, str):
        splitted = content.split('\n')
        if len(splitted) != 2:
            return None, "invalid doc format"
        try:
            m = re.match(DocInfo.USERNAME_RE, splitted[0])
            username = m.group(1)
            m = re.search(DocInfo.BIO_RE, splitted[1])
            bio = m.group(1)
        except Exception as e:
            return None, "invalid doc format"
        return DocInfo(username, bio), None


if __name__ == '__main__':
    checker.run()
