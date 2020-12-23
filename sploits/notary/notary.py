#!/usr/bin/env python3

import gmpy
import struct
import collections


Public = collections.namedtuple('Public', ['N', 'e'])
Private = collections.namedtuple('Private', ['N', 'p', 'q', 'e', 'd'])

Point = collections.namedtuple('Point', ['x', 'y'])
Curve = collections.namedtuple('Curve', ['a', 'b', 'q'])

ZERO = Point(0, 0)


def point_double(point, curve):
    if point == ZERO:
        return ZERO

    l = ((3 * point.x * point.x + curve.a) * gmpy.invert(2 * point.y, curve.q)) % curve.q

    x = (l * l - point.x - point.x) % curve.q
    y = (l * (point.x - x) - point.y) % curve.q

    return Point(x, y)



def point_add(point1, point2, curve):
    if point1 == ZERO:
        return point2
    if point2 == ZERO:
        return point1

    if (point1.x == point2.x) and (point1.y != point2.y) or (point1.y == 0):
        return ZERO

    if point1.x == point2.x:
        return point_double(point1, curve)
    
    l = ((point1.y - point2.y) * gmpy.invert(point1.x - point2.x, curve.q)) % curve.q
    
    x = (l * l - point1.x - point2.x) % curve.q
    y = (l * (point1.x - x) - point1.y) % curve.q

    return Point(x, y)


def point_multiply(point, number, curve):
    r0 = ZERO
    r1 = point

    for i in reversed(range(curve.q.bit_length())):
        if (number >> i) & 1 == 0:
            r1 = point_add(r0, r1, curve)
            r0 = point_double(r0, curve)
        else:
            r0 = point_add(r0, r1, curve)
            r1 = point_double(r1, curve)
    
    return r0


def point_is_on_curve(point, curve):
    return ((point.y**2 - point.x**3 - curve.a * point.x - curve.b) % curve.q) == 0


def curve_from_point(point, N):
    a = 0
    b = (point.y**2 - point.x**3) % N
    q = N

    return Curve(a, b, q)


def data_to_point(data, q):
    q_length = (q.bit_length() - 1) // 8
    value = [0xFF] * (2 * q_length)
    i = 0

    for x in data:
        if i == len(value):
            i = 0
        value[i] ^= x
        i += 1
    
    x = gmpy.mpz(int.from_bytes(value[:q_length], 'little'))
    y = gmpy.mpz(int.from_bytes(value[q_length:], 'little'))

    return Point(x, y)


def memfrob(data):
    result = list(data)

    xor = 0
    value = 1

    for i in reversed(range(len(result))):
        result[i] ^= value
        xor ^= result[i]
        value = (value * 11) % 251

    return bytes(result)

    
def load_numbers(data):
    data = memfrob(data)

    numbers = []

    while len(data) >= 4:
        size = struct.unpack('<I', data[:4])[0]
        number_data = data[4:4+size]
        if len(number_data) < size:
            break
        number = gmpy.mpz(int.from_bytes(number_data, 'little'))
        numbers.append(number)
        data = data[4+size:]    
    
    return numbers


def pack_numbers(*numbers):
    data = []

    for number in map(int, numbers):
        number_data = number.to_bytes((number.bit_length() + 7) // 8, 'little')
        data.append(struct.pack('<I', len(number_data)))
        data.append(number_data)

    return memfrob(b''.join(data))


def create_sign(private, data):
    N, p, q, e, d = load_numbers(data)
    point = data_to_point(data, N)
    curve = curve_from_point(point, N)
    sign = point_multiply(point, d, curve)
    return pack_numbers(sign.x, sign.y)


def verify_sign(public, data, sign):
    N, e = load_numbers(public)
    sign = Point(*load_numbers(sign))
    point = data_to_point(data, public.N)
    curve = curve_from_point(point, public.N)

    if not point_is_on_curve(sign, curve):
        return False

    data_expected = point_multiply(sign, e, curve)

    if point == data_expected:
        return True
