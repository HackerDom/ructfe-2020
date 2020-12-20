#!/usr/bin/python3
import string
import random

from gornilo import Checker, CheckRequest, PutRequest, GetRequest, Verdict
from api import Api
import proto.office_pb2 as pb
import json

checker = Checker()


def get_random_str(lenght=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=lenght))


def create_doc():
    return \
"""vars:
exprs:
  - name: "bio"
    expr: "get_info('bio')"
  - name: "token"
    expr: "get_info('token')"
---
<h1>Hi {username}!</h1>

<table>
  <tr>
    <td>Bio:</td>
    <td>'{bio}'</td>
  </tr>
  <tr>
    <td>Token:</td>
    <td>'{token}'</td>
  </tr>
</table>
"""


@checker.define_check
async def check_service(request: CheckRequest) -> Verdict:
    api = Api(f'{request.hostname}:8080')
    req = pb.ListDocumentsRequest()
    req.offset = 0
    req.limit = 100
    print(f"CHECK: '{req}'")
    r = api.list_doc(req)
    print(r.text)
    return Verdict.OK()


@checker.define_put(vuln_num=1, vuln_rate=2)
async def put(request: PutRequest) -> Verdict:
    api = Api(f'{request.hostname}:8080')
    req = pb.CreateDocumentRequest()
    req.name = get_random_str()
    req.doc = create_doc()
    print(f"PUT: '{req}'")
    r = api.create_doc(req)
    print(r.text)
    resp = json.loads(r.text)
    return Verdict.OK(f"{resp['id']}:{resp['token']}")


@checker.define_get(vuln_num=1)
async def get(request: GetRequest) -> Verdict:
    api = Api(f'{request.hostname}:8080')
    id, token = request.flag_id.split(":")
    req = pb.ExecuteRequest()
    username = get_random_str()
    req.doc_id = id
    req.username = username
    print(f"GET: '{id}':'{username}'")
    r = api.execute_doc(req)
    print(r.text)
    return Verdict.OK()


if __name__ == '__main__':
    checker.run()
