#!/usr/bin/env python3

import hashlib
import json
import random
import string
import sys
from functools import wraps

from faker import Faker
from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest

from client import CheckFailed, Client, corrupt, DocumentInfo, mumble, UserInfo


fake = Faker()


def generate_user():
    profile = fake.profile()
    return UserInfo(
        username=profile['username'],
        name=profile['name'],
        phone=fake.phone_number(),
        address=profile['address'])


def generate_document():
    return DocumentInfo(
        title=fake.sentence(),
        text=fake.text(max_nb_chars=400))


def hash_dict(dictionary):
    data = json.dumps(dictionary, sort_keys=True)
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


checker = Checker()


def create_user(client: Client, flag=None):
    user = generate_user()
    if flag is not None:
        user.address = flag
    registered_user = client.register(
        username=user.username, name=user.name, phone=user.phone, address=user.address)
    user.password = registered_user.password
    user.id = registered_user.id
    user.public_key = registered_user.public_key
    user.private_key = registered_user.private_key
    return user


def create_document(client: Client, public=False, flag=None):
    doc = generate_document()
    if flag is not None:
        doc.text = flag
    doc_id, password = client.sign(title=doc.title, text=doc.text, public=public)
    doc.id = doc_id
    doc.password = password
    return doc


def check_user_profile(anonymous_client, user, expected_docs):
    profile = anonymous_client.user(user.id)

    with mumble('checking user\'s document list'):
        for doc in expected_docs:
            assert doc.title.encode('utf-8') in profile, 'titles missing'
            assert f'doc/{doc.id}'.encode('utf-8') in profile, 'links missing'

    with mumble('checking public profile info'):
        for key in ('username', 'name', 'public_key'):
            value = getattr(user, key)
            assert value.encode('utf-8') in profile, f'{key} is missing'

    loaded_user = anonymous_client.log_in(user.username, user.password)

    with mumble('checking private profile info'):
        for key in ('phone', 'address', 'private_key'):
            value = getattr(user, key)
            assert getattr(loaded_user, key) == value, f'{key} changed'


def check_doc_access(anonymous_client, logged_in_client, doc_info):
    loaded_doc = anonymous_client.doc(doc_info.id, password=doc_info.password)
    with mumble('checking access to a document'):
        assert loaded_doc.text is not None, 'could not load text'
        assert loaded_doc.text == doc_info.text, 'document text changed'

    if doc_info.password is not None:
        loaded_doc = logged_in_client.doc(doc_info.id)
        with mumble('checking access to a document as its author'):
            assert loaded_doc.text is not None, 'could not load text'
            assert loaded_doc.text == doc_info.text, 'document text changed'


def check_doc_visibility(anonymous_client, expected_docs):
    feed = anonymous_client.feed()
    with mumble('checking doc visibility'):
        for doc in expected_docs:
            assert doc.title.encode('utf-8') in feed, 'titles missing'
            assert f'doc/{doc.id}'.encode('utf-8') in feed, 'links missing'


DEBUG = False


def errors_to_verdicts(f):
    @wraps(f)
    def wrapper(request):
        if DEBUG:
            return f(request)

        try:
            result = f(request)
        except CheckFailed as err:
            return Verdict(err.verdict, err.reason)

        if result is not None:
            return result
        return Verdict.OK()

    return wrapper


@checker.define_check
@errors_to_verdicts
def check_service(request: CheckRequest) -> Verdict:
    client = Client(request.hostname)
    user = create_user(client)
    public_doc = create_document(client, public=True)
    private_doc = create_document(client, public=False)

    check_user_profile(Client(request.hostname), user, (public_doc, private_doc))
    check_doc_access(Client(request.hostname), client, public_doc)
    check_doc_access(Client(request.hostname), client, private_doc)
    check_doc_visibility(Client(request.hostname), (public_doc, private_doc))


@checker.define_put(vuln_num=1, vuln_rate=1)
@checker.define_put(vuln_num=2, vuln_rate=1)
@errors_to_verdicts
def put_flag(request: PutRequest) -> Verdict:
    client = Client(request.hostname)
    if request.vuln_id == 1:
        user = create_user(client, flag=request.flag)
        doc = create_document(client, public=True)
    else:
        user = create_user(client)
        doc = create_document(client, public=False, flag=request.flag)

    info_hash = hash_dict(dict(user=vars(user), doc=vars(doc)))
    flag_id = dict(
        username=user.username, password=user.password,
        doc_id=doc.id, doc_password=doc.password,
        hash=info_hash)
    return Verdict.OK(flag_id=json.dumps(flag_id))


@checker.define_get(vuln_num=1)
@checker.define_get(vuln_num=2)
@errors_to_verdicts
def get_flag(request: GetRequest) -> Verdict:
    client = Client(request.hostname)
    flag_id = json.loads(request.flag_id)

    user = client.log_in(flag_id['username'], flag_id['password'])
    doc = client.doc(flag_id['doc_id'])
    doc.password = flag_id['doc_password']

    if request.vuln_id == 1:
        actual_flag = user.address
    else:
        actual_flag = doc.text
    with corrupt(None):
        assert request.flag == actual_flag, 'A flag is missing'

    info_hash = hash_dict(dict(user=vars(user), doc=vars(doc)))
    with mumble('checking data consistency'):
        assert info_hash == flag_id['hash'], 'either a user\'s profile or a document\'s content changed'

    check_user_profile(Client(request.hostname), user, (doc,))
    check_doc_access(Client(request.hostname), client, doc)
    check_doc_visibility(Client(request.hostname), (doc,))


def test_run():
    global DEBUG
    DEBUG = True
    hostname = 'localhost'

    print('Checking...')
    check_service(CheckRequest(hostname))

    for vuln_id in (1, 2):
        flag = ''.join(random.choices(string.ascii_uppercase, k=31)) + '='
        print(f'\nvuln_id={vuln_id}, flag={flag}')
        print('Putting...')
        flag_id = put_flag(PutRequest('', flag, vuln_id, hostname))._public_message
        print(flag_id)

        print('Getting...')
        get_flag(GetRequest(flag_id, flag, vuln_id, hostname))

    print('\nSuccess!')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        checker.run()
    else:
        test_run()
