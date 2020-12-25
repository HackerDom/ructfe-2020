#!/usr/bin/env python3

import json
import random
import string
import sys
from functools import wraps

from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest

from client import Client
from utils import CheckFailed, corrupt, DocumentInfo, generate_document, generate_user, hash_dict, mumble, UserInfo
from verify_crypto import Verify


def check_user_crypto(user: UserInfo):
    with mumble('checking a user\'s cryptographic data for integrity'):
        assert Verify.public_key(user.public_key), 'public key is invalid'
        assert Verify.private_key(user.private_key), 'private key is invalid'
        assert Verify.key_pair(user.private_key, user.public_key), 'key pair is invalid'
        assert Verify.user_password(user.password, user.username), 'password is invalid'


def check_doc_crypto(doc: DocumentInfo):
    with mumble('checking a document\'s cryptographic data for integrity'):
        assert Verify.signature(doc.signature, doc.text), 'signature is invalid'
        if doc.password is not None:
            assert Verify.document_password(doc.password, doc.id), 'password is invalid'


def create_user(client: Client, flag=None):
    user = generate_user()
    if flag is not None:
        user.address = flag
    user = client.register(
        username=user.username, name=user.name, phone=user.phone, address=user.address)
    check_user_crypto(user)
    return user


def create_document(client: Client, author_id, public=False, flag=None):
    doc = generate_document()
    if flag is not None:
        doc.text = flag
    doc = client.sign(title=doc.title, text=doc.text, author_id=author_id, public=public)
    check_doc_crypto(doc)
    return doc


def assert_fields_equal(user, loaded_user, fields):
    for key in fields:
        expected_value = getattr(user, key)
        loaded_value = getattr(loaded_user, key)
        assert loaded_value, f'{key} is missing'
        assert loaded_value == expected_value, f'{key} has an unexpected value'


def assert_links_not_missing(doc_ids, expected_docs):
    expected_ids = [doc.id for doc in expected_docs]
    assert set(expected_ids) <= set(doc_ids), 'links to some documents missing'


def check_user_document_list(loaded_user, expected_docs):
    with mumble('checking a user\'s document list'):
        assert_links_not_missing(loaded_user.document_ids, expected_docs)


def check_user_profile_publicly(anonymous_client, user, expected_docs):
    loaded_user = anonymous_client.user(user.id)
    check_user_document_list(loaded_user, expected_docs)
    with mumble('checking public profile info'):
        assert_fields_equal(user, loaded_user, ('username', 'name', 'public_key'))


def check_user_profile_privately(anonymous_client, user, expected_docs):
    loaded_user = anonymous_client.log_in(user.username, user.password)
    check_user_document_list(loaded_user, expected_docs)
    with mumble('checking private profile info'):
        assert_fields_equal(user, loaded_user, ('phone', 'address', 'private_key'))


def check_doc_access(anonymous_client, logged_in_client, doc_info):
    if doc_info.password is not None:
        loaded_doc = anonymous_client.doc(doc_info.id)
        with mumble('checking anonymous access to a private document'):
            assert_fields_equal(doc_info, loaded_doc, ('title', 'author_id'))

        loaded_doc = logged_in_client.doc(doc_info.id)
        with mumble('checking access to a private document as its author'):
            assert_fields_equal(doc_info, loaded_doc, ('title', 'text', 'author_id', 'signature'))

    loaded_doc = anonymous_client.doc(doc_info.id, password=doc_info.password)
    with mumble('checking access to a document'):
        assert_fields_equal(doc_info, loaded_doc, ('title', 'text', 'author_id', 'signature'))


def check_doc_visibility(anonymous_client, expected_docs):
    with mumble('checking feed content'):
        assert_links_not_missing(anonymous_client.feed(), expected_docs)


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


checker = Checker()


@checker.define_check
@errors_to_verdicts
def check_service(request: CheckRequest) -> Verdict:
    public_client = Client(request.hostname)
    private_client = Client(request.hostname)
    public_user = create_user(public_client)
    private_user = create_user(private_client)
    public_doc = create_document(public_client, author_id=public_user.id, public=True)
    private_doc = create_document(private_client, author_id=private_user.id, public=False)

    check_user_profile_privately(Client(request.hostname), public_user, (public_doc,))
    check_user_profile_publicly(Client(request.hostname), private_user, (private_doc,))
    check_doc_access(Client(request.hostname), public_client, public_doc)
    check_doc_access(Client(request.hostname), private_client, private_doc)
    check_doc_visibility(Client(request.hostname), (public_doc, private_doc))


@checker.define_put(vuln_num=1, vuln_rate=1)
@checker.define_put(vuln_num=2, vuln_rate=1)
@errors_to_verdicts
def put_flag(request: PutRequest) -> Verdict:
    client = Client(request.hostname)
    if request.vuln_id == 1:
        user = create_user(client, flag=request.flag)
        doc = create_document(client, author_id=user.id, public=True)
    else:
        user = create_user(client)
        doc = create_document(client, author_id=user.id, public=False, flag=request.flag)

    user.document_ids = []  # Don't need to compare them
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

    user.document_ids = []
    info_hash = hash_dict(dict(user=vars(user), doc=vars(doc)))
    with mumble('checking data consistency'):
        assert info_hash == flag_id['hash'], 'either a user\'s profile or a document\'s content changed'

    if request.vuln_id == 1:
        check_user_profile_privately(Client(request.hostname), user, (doc,))
    else:
        check_user_profile_publicly(Client(request.hostname), user, (doc,))
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
