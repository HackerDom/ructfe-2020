import random


def gen_privkey():
    return 'priv' + str(random.randint(0, 2 ** 32 - 1))


def get_pubkey_from_privkey(privkey):
    return 'pub' + privkey[4:]


def create_signature(privkey, title, text):
    data = title + '|' + text.replace('|', '\\|')
    return f'signature for {data}: {privkey}'


def verify_signature(pubkey, title, text, signature):
    data = title + '|' + text.replace('|', '\\|')
    return signature == f'signature for {data}: priv{pubkey[3:]}'
