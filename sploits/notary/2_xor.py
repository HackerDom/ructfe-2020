#!/usr/bin/env python3

import base64
import notary
import string


alpha = set(map(ord, string.ascii_letters + string.digits))


def get_xor_pair(x):
    for y in alpha:
        if x ^ y in alpha:
            return y, x ^ y


def forge_data(length, data, expected_prefix, expected_suffix):
    data = notary.compress_data(data, length)
    
    prefix = expected_prefix.ljust(2 * length, b'X')
    suffix = expected_suffix.rjust(2 * length, b'X')

    middle = [[], []]

    for i, (x, y) in enumerate(zip(prefix, suffix)):
        pair = get_xor_pair(0xFF ^ x ^ y ^ data[i])
        for mid, val in zip(middle, pair):
            mid.append(val)
    
    return prefix + b''.join(map(bytes, middle)) + suffix


def main():
    private_key = base64.b64decode('2AhcNnbvcSo57TAIMh+9+TpZZw0pAleL2vhZqK9iDvlyKI6hjVgZuoJeIiDLPtMqEJE9vJrwTuKU90dT4oKqNBJ9DrOkpQ/XWz6YKA3I3svhnlQ9SiK7onOnDTfWcNo2vxVaxLmXqbEQSSQ5PBowcpnTs7AQuuwunB2mbltDDGA6e/N1ETXpLPvR5EYKSaqc9hoGGw8hA6BTTHkLAYk9koO0VCm+h4LGHUd91y7sokDAnhKl4Bjqi7AfXk2HMZH1DCGpEzOohWuE9kQdL3pqLb6xmYDZb5M7M9KcJTG70bnLn5ttUpSa34onHjTWsidISwu8cPLn5l2VKKf3o8kIL45VOe0wCDIfvfm6WZvyFgIWi9t4W6ivg/AFjTiOgK+nJkV8fsIgS/4vd+s8wOGZrF22k3IvhsTCeFQE36PGFYfFNJLNfVVsKUiaxm7bT9PMEtxJridQLQtGM5fM0RtHrvYJrhRph2ZjS/FQdKscioOZi8ZSgY4QrbfdepVvuJwFe/IpoFCDTXN40QXqIlZU7HdSKEH9+Xo=')
    N, p, q, e, d = notary.load_numbers(private_key)

    original_data = b'Lorem ipsum, dolor sit amet... ' * 10
    original_signature = notary.create_sign(private_key, original_data)

    public_key = notary.pack_numbers(N, e)

    length = (N.bit_length() - 1) // 8
    fake_data = forge_data(length, original_data, b'{"username": "admin", "fake": "', b'"}')

    print('Original:', original_data)
    print('Fake:', fake_data)
    
    print(notary.verify_sign(public_key, fake_data, original_signature))


if __name__ == '__main__':
    main()
