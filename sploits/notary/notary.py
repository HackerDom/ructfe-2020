#!/usr/bin/env python3

import math
import struct
import base64
import msgpack

from dataclasses import dataclass
from Crypto.Util.number import isPrime, inverse


class InvalidCryptoException(Exception):
    pass


def memfrob(data):
    result = list(data)

    xor, value = 0, 1

    for i in reversed(range(len(result))):
        result[i] ^= value
        xor ^= result[i]
        value = (value * 11) % 251

    return bytes(result)


class Numbers:
    @staticmethod
    def pack(*numbers):
        data = []

        for number in numbers:
            size = (number.bit_length() + 7) // 8
            number_data = number.to_bytes(size, 'little')
            data.append(struct.pack('<I', len(number_data)))
            data.append(number_data)

        return memfrob(b''.join(data))

    @staticmethod
    def unpack(data):
        data = memfrob(data)

        numbers = []

        while len(data) >= 4:
            size = struct.unpack('<I', data[:4])[0]
            number_data = data[4:4+size]
            
            if len(number_data) < size:
                break
            
            number = int.from_bytes(number_data, 'little')
            numbers.append(number)
            data = data[4+size:]    
        
        return numbers


class Bytes:
    @staticmethod
    def pack(data):
        return base64.urlsafe_b64encode(data).decode('utf-8')
    
    @staticmethod
    def unpack(data):
        try:
            return base64.urlsafe_b64decode(data)
        except Exception:
            raise InvalidCryptoException


class Objects:
    @staticmethod
    def pack(obj):
        return Bytes.pack(msgpack.dumps(obj))
    
    @staticmethod
    def unpack(data):
        data = Bytes.unpack(data)

        try:
            return msgpack.loads(data)
        except Exception:
            raise InvalidCryptoException


@dataclass
class Public:
    N: int
    e: int

    def pack(self):
        return Bytes.pack(Numbers.pack(self.N, self.e))

    @staticmethod
    def unpack(data):
        data = Bytes.unpack(data)

        try:
            numbers = Numbers.unpack(data)
        except Exception:
            raise InvalidCryptoException

        if len(numbers) != 2:
            raise InvalidCryptoException

        return Public(*numbers)


@dataclass
class Private:
    N: int
    p: int
    q: int
    e: int
    d: int

    def pack(self):
        return Bytes.pack(Numbers.pack(self.N, self.p, self.q, self.e, self.d))

    @staticmethod
    def unpack(data):
        data = Bytes.unpack(data)

        try:
            numbers = Numbers.unpack(data)
        except Exception:
            raise InvalidCryptoException

        if len(numbers) != 5:
            raise InvalidCryptoException

        return Private(*numbers)

    def is_valid(self):
        if not isPrime(self.p) or not isPrime(self.q):
            return False

        if self.p % 3 != 2 or self.q % 3 != 2:
            return False

        if self.p * self.q != self.N:
            return False

        phi = (self.p + 1) * (self.q + 1)

        if math.gcd(self.e, phi) != 1 or (self.e * self.d) % phi != 1:
            return False

        return True

    def get_public(self):
        return Public(self.N, self.e)

    
@dataclass
class Point:
    x: int
    y: int

    def pack(self):
        return Bytes.pack(Numbers.pack(self.x, self.y))

    @staticmethod
    def unpack(data):
        data = Bytes.unpack(data)

        try:
            numbers = Numbers.unpack(data)
        except Exception:
            raise InvalidCryptoException

        if len(numbers) != 2:
            raise InvalidCryptoException

        return Point(*numbers)


@dataclass
class Curve:
    a: int
    b: int
    q: int

    def pack(self):
        return Bytes.pack(Numbers.pack(self.a, self.b, self.q))

    @staticmethod
    def unpack(data):
        data = Bytes.unpack(data)

        try:
            numbers = Numbers.unpack(data)
        except Exception:
            raise InvalidCryptoException

        if len(numbers) != 3:
            raise InvalidCryptoException

        return Public(*numbers)

    @staticmethod
    def from_point(point, N):
        a = 0
        b = (point.y**2 - point.x**3) % N
        q = N

        return Curve(a, b, q)

    def is_valid(self):
        return (4 * (self.a ** 3) + 27 * (self.b ** 2)) % self.q != 0

    def has_point(self, point):
        return ((point.y**2 - point.x**3 - self.a * point.x - self.b) % self.q) == 0


@dataclass
class Document:
    obj: object
    data: bytes
    signature: Point

    def pack(self):
        return f'{Objects.pack(self.obj)}.{self.signature.pack()}'

    @staticmethod
    def unpack(data):
        try:
            obj_data, signature = data.split('.')
            return Document(Objects.unpack(obj_data), Bytes.unpack(obj_data), Point.unpack(signature))
        except Exception:
            raise InvalidCryptoException


class Hash:
    @staticmethod
    def data_to_point(data, N):
        length = (N.bit_length() + 7) // 8
    
        value = [0xFF] * (2 * length)
        i = 0

        for x in data:
            if i == len(value):
                i = 0
            value[i] ^= x
            i += 1

        value = bytes(value)
        
        x = int.from_bytes(value[:length], 'little')
        y = int.from_bytes(value[length:], 'little')

        return Point(x % N, y % N)

    @staticmethod
    def point_to_data(point, N):
        length = (N.bit_length() + 7) // 8
    
        x_data = point.x.to_bytes(length, 'little')
        y_data = point.y.to_bytes(length, 'little')

        return x_data + y_data


class Elliptic:
    Identity = Point(0, 0)

    @staticmethod
    def inverse(point, curve):
        return Point(point.x, (-point.y) % curve.q)

    @staticmethod
    def double(point, curve):
        if point == Elliptic.Identity:
            return Elliptic.Identity

        l = ((3 * point.x * point.x + curve.a) * inverse(2 * point.y, curve.q)) % curve.q

        x = (l * l - 2 * point.x) % curve.q
        y = (l * (point.x - x) - point.y) % curve.q

        return Point(x, y)

    @staticmethod
    def add(point1, point2, curve):
        if point1 == Elliptic.Identity:
            return point2
        if point2 == Elliptic.Identity:
            return point1

        if (point1.x == point2.x) and (point1.y != point2.y) or (point1.y == 0):
            return Elliptic.Identity

        if point1.x == point2.x:
            return Elliptic.double(point1, curve)
        
        l = ((point1.y - point2.y) * inverse(point1.x - point2.x, curve.q)) % curve.q
        
        x = (l * l - point1.x - point2.x) % curve.q
        y = (l * (point1.x - x) - point1.y) % curve.q

        return Point(x, y)

    @staticmethod
    def multiply(point, number, curve):
        r0 = Elliptic.Identity
        r1 = point

        if number < 0:
            r1 = Elliptic.inverse(r1, curve)
            number = abs(number)

        for i in reversed(range(curve.q.bit_length())):
            if (number >> i) & 1 == 0:
                r1 = Elliptic.add(r0, r1, curve)
                r0 = Elliptic.double(r0, curve)
            else:
                r0 = Elliptic.add(r0, r1, curve)
                r1 = Elliptic.double(r1, curve)

        return r0


class Signature:
    @staticmethod
    def exclude_identity(point, curve):
        default_x, default_y = 31337, 31337

        if point == Elliptic.Identity or not curve.is_valid():
            point = Point(default_x, default_y)
            curve = Curve.from_point(point, curve.q)

        return point, curve

    @staticmethod
    def create(private, data):
        point = Hash.data_to_point(data, private.N)
        curve = Curve.from_point(point, private.N)
        point, curve = Signature.exclude_identity(point, curve)

        signature = Elliptic.multiply(point, private.d, curve)
        
        return Numbers.pack(signature.x, signature.y)

    @staticmethod
    def verify(public, data, signature):
        if signature == Elliptic.Identity:
            return False

        point = Hash.data_to_point(data, public.N)
        curve = Curve.from_point(point, public.N)
        point, curve = Signature.exclude_identity(point, curve)

        if not curve.has_point(signature):
            return False

        data_expected = Elliptic.multiply(signature, public.e, curve)

        if point == data_expected:
            return True

        return False
