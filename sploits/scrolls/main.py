import random
import string
import sys

from api import Api
import proto.office_pb2 as pb


def create_doc(name):
    return f"""
vars:
  username: {name}
exprs:
  - name: bio
    expr: "get_info('bio')"
---
{{bio}}
'"""


def get_random_str(length=10, only_chars=False):
    if only_chars:
        return "".join(random.choices(string.ascii_letters, k=length))
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


IP = sys.argv[1]
PORT = ':8080'
a = Api(IP + PORT)


def list():
    users = []
    offset = 0
    while True:
        req = pb.ListRequest()
        req.offset = offset
        req.limit = 3000
        r, err = a.list_users(req)
        if err != None:
            print(err)
            return users
        if not hasattr(r, 'usernames'):
            print("invalid users listing")
            return users
        users += r.usernames
        if len(r.usernames) < 3000:
            return users
        offset += 3000


req = pb.RegisterRequest()
req.name = get_random_str()
req.password = get_random_str()
req.bio = get_random_str()
a.register(req)

users = list()

for name in users:
    doc = create_doc(name)
    req = pb.TestDocRequest()
    req.content = doc
    r, err = a.test_doc(req)
    print(r)
