import dataclasses
import hashlib
import json
import random
import string
from contextlib import contextmanager
from dataclasses import dataclass, field

import requests
from faker import Faker
from gornilo.models.verdict.verdict_codes import MUMBLE, CORRUPT, DOWN
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import Any


@dataclass
class UserInfo:
    username: str = None
    name: str = None
    phone: str = None
    address: str = None
    id: str = None
    password: str = None
    public_key: str = None
    private_key: str = None
    document_ids: [str] = None


@dataclass
class DocumentInfo:
    title: str = None
    text: str = None
    id: str = None
    password: str = None
    author_id: str = None
    signature: str = None


def hash_dict(dictionary):
    data = json.dumps(dictionary, sort_keys=True)
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


@dataclass
class ExecutionContext:
    username: str = None
    password: str = None
    doc_id: str = None
    doc_password: str = None
    details: [Any] = field(default_factory=list)

    def set_user(self, user=None, username=None, password=None):
        if user is not None:
            username = user.username
            password = user.password
        self.username = username
        self.password = password

    def reset_user(self):
        self.username = self.password = None

    def set_document(self, doc=None, doc_id=None, password=None):
        if doc is not None:
            doc_id = doc.id
            password = doc.password
        self.doc_id = doc_id
        self.doc_password = password

    def reset_document(self):
        self.doc_id = self.doc_password = None

    def reset(self):
        self.reset_user()
        self.reset_document()
        self.details = []

    def set(self, user=None, doc=None):
        self.reset()
        self.set_user(user)
        self.set_document(doc)

    def copy(self):
        return ExecutionContext(
            username=self.username, password=self.password,
            doc_id=self.doc_id, doc_password=self.doc_password,
            details=self.details[:])

    @classmethod
    def _trim_text(cls, text):
        if text is None:
            return None
        return text[:30]

    @classmethod
    def _clean_detail(cls, detail):
        if isinstance(detail, tuple):
            return tuple(map(cls._clean_detail, detail))
        if isinstance(detail, DocumentInfo):
            return dataclasses.replace(
                detail, title=cls._trim_text(detail.title), text=cls._trim_text(detail.text))
        return detail

    def print(self):
        print('Context:')
        for field in ('username', 'password', 'doc_id', 'doc_password'):
            print(f'{field}={getattr(self, field)}')
        for i in range(len(self.details) - 1, -1, -1):
            print(f'Detail #{i}: {self._clean_detail(self.details[i])}')


CONTEXT = ExecutionContext()


class CheckFailed(ValueError):
    def __init__(self, verdict, reason, context):
        self.verdict = verdict
        self.reason = reason
        self.context = context


@contextmanager
def check(verdict, phase_name=None, exc_messages=None, details=None):
    if exc_messages is None:
        exc_messages = {}
    if isinstance(exc_messages, set):
        exc_messages = {exc_type: None for exc_type in exc_messages}
    exc_types = tuple(exc_messages.keys())

    reason = None
    try:
        CONTEXT.details.append(details)
        yield
        return
    except AssertionError as err:
        context = CONTEXT.copy()
        e = err
        if err.args:
            reason = err.args[0]
    except Exception as err:
        if not isinstance(err, exc_types):
            raise
        context = CONTEXT.copy()
        e = err
        reason = None
        for exc_type, message in exc_messages.items():
            if isinstance(err, exc_type):
                reason = message
        if reason is None:
            reason = type(err).__name__
    finally:
        CONTEXT.details.pop()

    context.details.append((type(e), str(e)))
    prefix = ''
    if phase_name is not None:
        prefix = f'Failed while {phase_name}'
    suffix = reason or ''
    colon = ''
    if prefix and suffix:
        colon = ': '
    raise CheckFailed(verdict, prefix + colon + suffix, context) from e


def mumble(phase_name=None, exc_messages=None, details=None):
    return check(MUMBLE, phase_name, exc_messages, details=details)


def corrupt(phase_name=None, exc_messages=None, details=None):
    return check(CORRUPT, phase_name, exc_messages, details=details)


def down(phase_name=None, exc_messages=None, details=None):
    return check(DOWN, phase_name, exc_messages, details=details)


ARAB_FAKE = Faker('ar_AA')
ENGLISH_FAKE = Faker()
ARAB_PROBABILITY = 0.15
PRINTABLE = set(string.printable)


def select_fake():
    return ARAB_FAKE if random.random() < ARAB_PROBABILITY else ENGLISH_FAKE


def generate_user():
    fake = select_fake()
    profile = fake.profile()
    return UserInfo(
        username=profile['username'][:16] + ''.join(random.choices(string.digits, k=7)),
        name=profile['name'],
        phone=fake.phone_number(),
        address=profile['address'])


def generate_document(author_name=None):
    if author_name is None:
        fake = select_fake()
    elif any(sym not in PRINTABLE for sym in author_name):
        fake = ARAB_FAKE
    else:
        fake = ENGLISH_FAKE
    return DocumentInfo(
        title=fake.sentence(),
        text=fake.text(max_nb_chars=400))


def requests_with_retry(retries=3, backoff_factor=0.3, status_forcelist=(400, 404, 500, 502), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    return session
