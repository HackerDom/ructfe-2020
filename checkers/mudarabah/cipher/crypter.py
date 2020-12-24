import numpy as np

from math import factorial, log
from random import randint
from struct import pack, unpack

from cipher.code import LDPC
from cipher.utils import bytes_to_codeword, codeword_to_bytes, dump, gaussjordan, load


class Crypter:
    def __init__(self, code, S, P, errors=10):
        self.S = S
        self.P = P
        self.errors = errors

        self.code = code

        self.k, self.n = code.G.shape
                
        self.public_key = self.S @ self.code.G @ self.P % 2

    @classmethod 
    def from_code(cls, code: LDPC):
        k, n = code.G.shape

        P = np.eye(n, dtype=int) 
        np.random.shuffle(P) 

        S = Crypter._get_non_singular_random_matrix(k)

        return cls(code, S, P)

    def encrypt(self, pt):
        pt_word = bytes_to_codeword(pt, self.code.G.shape[0])
        z = np.array([1 for _ in range(self.errors)] + [0 for _  in range(self.n - self.errors)], dtype=int)
        np.random.shuffle(z)
        return codeword_to_bytes(((pt_word @ self.public_key % 2) + z) % 2)

    def decrypt(self, ct):
        ct_word = bytes_to_codeword(ct, self.code.G.shape[1])

        A, invP = gaussjordan(self.P, True)

        c = np.array(ct_word @ invP % 2, dtype=int)

        d = self.code.decode(c)
        m = self.code.get_message(d)

        _, invS = gaussjordan(self.S, True)

        return codeword_to_bytes(m @ invS % 2)

    @staticmethod
    def _get_non_singular_random_matrix(k):
        while True:
            S = np.random.randint(0, 2, (k, k)) 

            A = gaussjordan(S)
            A = np.array(A, dtype=int)

            if (A == np.eye(k, dtype=int)).all():
                return S

    def dump_private(self):
        matrixes = [self.S, self.P, self.code.G, self.code.H]
        return b''.join((pack('<H', len(x)) + x) for x in map(dump, matrixes))

    def dump_public(self):
        pub_dump = dump(self.public_key)
        return pack('<H', len(pub_dump)) + pub_dump

    @classmethod
    def load_private(cls, data):
        matrixes = []
        while data:
            size = unpack('<H', data[:2])[0]
            dump, data = data[2:size+2], data[size+2:]
            matrixes.append(load(dump))
        S, P, G, H = matrixes
        return cls(LDPC(G, H), S, P)