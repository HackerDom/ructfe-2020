import base64

import libnotary


def serialize_bytes(bs):
    return base64.b64encode(bs).decode('utf-8')


def deserialize_bytes(string):
    try:
        return base64.b64decode(string)
    except ValueError as err:
        raise ValueError('Failed to deserialize bytes') from err


def pack_document(title, text):
    return title + '|' + text.replace('|', '\\|')


def gen_privkey():
    key = libnotary.generate()
    if key is None:
        raise ValueError('Failed to generate a private key')
    return serialize_bytes(key)


def get_pubkey_from_privkey(privkey):
    pubkey = libnotary.get_public(deserialize_bytes(privkey))
    if pubkey is None:
        raise ValueError('Invalid private key')
    return serialize_bytes(pubkey)


def create_signature(privkey, title, text):
    signature = libnotary.sign(
        deserialize_bytes(privkey),
        pack_document(title, text).encode('utf-8'))
    if signature is None:
        raise ValueError('Invalid private key')
    return serialize_bytes(signature)


def verify_signature(pubkey, title, text, signature):
    try:
        pubkey = deserialize_bytes(pubkey)
        signature = deserialize_bytes(signature)
    except ValueError:
        return False  # Garbage input

    result = libnotary.verify(pubkey, pack_document(title, text).encode('utf-8'), signature)
    if result is None:
        return False  # The public key is invalid, makes sense to return False
    return result


# import random
#
#
# def gen_privkey():
#     return 'priv' + str(random.randint(0, 2 ** 32 - 1))
#
#
# def get_pubkey_from_privkey(privkey):
#     return 'pub' + privkey[4:]
#
#
# def create_signature(privkey, title, text):
#     data = pack_document(title, text)
#     return f'signature for {data}: {privkey}'
#
#
# def verify_signature(pubkey, title, text, signature):
#     data = pack_document(title, text)
#     return signature == f'signature for {data}: priv{pubkey[3:]}'
