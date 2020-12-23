#!/usr/bin/env python3

import math
import gmpy
import base64
import bisect
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


def recover_private_key(public_key):
    N, e = notary.load_numbers(public_key)
    p, q = factorize(N)
    phi = (p + 1) * (q + 1)
    d = int(gmpy.invert(e, phi))
    return notary.pack_numbers(N, p, q, e, d)


def main():
    public_key = base64.b64decode(input())
    private_key = recover_private_key(public_key)
    print(base64.b64encode(private_key))


if __name__ == '__main__':
    main()
