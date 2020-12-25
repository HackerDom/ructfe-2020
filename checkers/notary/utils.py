import hashlib
import json
from contextlib import contextmanager
from dataclasses import dataclass

from faker import Faker
from gornilo.models.verdict.verdict_codes import MUMBLE, CORRUPT, DOWN


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


class CheckFailed(ValueError):
    def __init__(self, verdict, reason):
        self.verdict = verdict
        self.reason = reason


@contextmanager
def check(verdict, phase_name=None, exc_messages=None):
    if exc_messages is None:
        exc_messages = {}
    if isinstance(exc_messages, set):
        exc_messages = {exc_type: None for exc_type in exc_messages}
    exc_types = tuple(exc_messages.keys())

    reason = None
    try:
        yield
    except AssertionError as err:
        e = err
        if err.args:
            reason = err.args[0]
    except Exception as err:
        if not isinstance(err, exc_types):
            raise
        e = err
        reason = None
        for exc_type, message in exc_messages.items():
            if isinstance(err, exc_type):
                reason = message
        if reason is None:
            reason = type(err).__name__
    else:
        return

    prefix = ''
    if phase_name is not None:
        prefix = f'Failed while {phase_name}'
    suffix = reason or ''
    colon = ''
    if prefix and suffix:
        colon = ': '
    raise CheckFailed(verdict, prefix + colon + suffix) from e


def mumble(phase_name=None, exc_messages=None):
    return check(MUMBLE, phase_name, exc_messages)


def corrupt(phase_name=None, exc_messages=None):
    return check(CORRUPT, phase_name, exc_messages)


def down(phase_name=None, exc_messages=None):
    return check(DOWN, phase_name, exc_messages)


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
