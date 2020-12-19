#!/usr/bin/env python3
import os
import re
import traceback
from sys import argv, stderr
import requests
import sys
from requests.exceptions import ConnectionError, HTTPError
import random
import string

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

vowels = list('aeiou')

def gen_word(min, max):
    word = ''
    syllables = min + int(random.random() * (max - min))
    for i in range(0, syllables):
        word += gen_syllable()
    
    return word.upper()


def gen_syllable():
    ran = random.random()
    if ran < 0.333:
        return word_part('v') + word_part('c')
    if ran < 0.666:
        return word_part('c') + word_part('v')
    return word_part('c') + word_part('v') + word_part('c')


def word_part(type):
    if type is 'c':
        return random.sample([ch for ch in list(string.ascii_lowercase) if ch not in vowels], 1)[0]
    if type is 'v':
        return random.sample(vowels, 1)[0]

def select_name():
    return gen_word(2, 6)


flag_alpha = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

spirits = [
"Ale",
"Porter",
"Stout",
"Lager",
"Cider",
"Mead",
"Wine",
"Port",
"Sherry",
"Vermouth",
"Vinsanto",
"Sangria",
"Champagne",
"Sake",
"Brandy",
"Cognac",
"Armagnac",
"Schnapps",
"Gin",
"Horilka",
"Metaxa",
"Rakia",
"Rum",
"Shochu",
"Soju",
"Tequila",
"Vodka",
"Bourbon",
"Whiskey",
"Absinthe",
"Juice",
"Cola",
"Water"
]

def parse_flag(flag):
    return [flag_alpha.index(c) for c in flag[:-1]]

def unparse_flag(l):
    l = ([0] * (31 - len(l))) + l
    return ''.join([flag_alpha[c] for c in l]) + '='

def parse_recipe(recipe):
    l = [spirits.index(c) for c in recipe]
    return ([0] * (len(spirits) - len(l))) + l

def unparse_recipe(l):
    return [spirits[c] for c in l]

def pack_cmd(op, a, b):
    return '%s;%x;%x;%x;%x;' % (op, (a >> 128) & 0xffffffffffffffff, (a >> 64) & 0xffffffffffffffff, (a) & 0xffffffffffffffff, b)
def unpack_result(s):
    d0, d1, d2, r = s.split(';')
    d = (int(d0, 16) << 128) | (int(d1, 16) << 64) | (int(d2, 16));
    return (d, int(r, 16))

def convert_base(x, base_from, base_to):
    n = 0
    for digit in x:
        n *= base_from
        n += digit

    #n = ~n & 0xffffffffffffffffffffffffffffffffffffffffffffffff
    n ^= 0xb0b8badbeefdefec87edfece5f100deda11dead

    l = []
    while n > 0:
        #n, value = divmod(n, base_to)
        value = n % base_to
        n = n // base_to
        l.append(value)
    l.reverse()

    return l

def flag_to_recipe(flag):
    return unparse_recipe(convert_base(parse_flag(flag), len(flag_alpha), len(spirits)))

def merge_bytes(s):
    m = 0
    for i in range(len(s)):
        m |= s[i] << 8 * i;
    return m

def hash_flag(flag):
    flag_copy = [0] * 32

    for i in range(32):
        idx = i if i % 2 == 0 else 32 - i
        flag_copy[idx] = ord(flag[i]) - ord('A') + 10 if flag[i] > '9' else ord(flag[i]) - ord('0')
    
    seed = 0x60d15dead
    m = 0xc6a4a7935bd1e995
    r = 47

    h = (seed ^ (32 * m)) & 0xffffffffffffffff

    data = [ merge_bytes(flag_copy[0:8]), merge_bytes(flag_copy[8:16]), merge_bytes(flag_copy[16:24]), merge_bytes(flag_copy[24:32]), ]

    for k in data:
        k = (k * m) & 0xffffffffffffffff
        k = (k ^ (k >> r)) & 0xffffffffffffffff
        k = (k * m) & 0xffffffffffffffff

        h = (h ^ k) & 0xffffffffffffffff
        h = (h * m) & 0xffffffffffffffff

    h = (h * m) & 0xffffffffffffffff

    h = (h ^ (h >> r)) & 0xffffffffffffffff
    h = (h * m) & 0xffffffffffffffff
    h = (h ^ (h >> r)) & 0xffffffffffffffff

    if (h >> 63) == 0:
        h = ~h & 0xffffffffffffffff

    return hex(h)[2:]


def print_to_stderr(*args):
    print(*args, file=sys.stderr)


def info():
    print("vulns: 1")
    exit(OK)


def check(hostname):
    exit(OK)


def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    return CHECKER_ERROR


def put(hostname, flag_id, flag, vuln):

    name = select_name()
    recipe = flag_to_recipe(flag)
    flag_hash = hash_flag(flag)

    exit_code = OK
    try:
        #TODO multiple selection attempts
        response = requests.get('http://%s:4280/memorize?name=%s&what=%s' % (hostname, name, ','.join(recipe)))
        response.raise_for_status()

        response = requests.get('http://%s:4280/list?skip=0&take=31' % hostname)
        response.raise_for_status()

        if not name in response.text:
            exit_code = CORRUPT
            print_to_stderr('New name "%s" was not listed' % name)
            exit(exit_code)

        response = requests.get('http://%s:4280/mix?name=%s' % (hostname, name))
        response.raise_for_status()

        if flag_hash != response.text:
            exit_code = CORRUPT
            print_to_stderr('Hash mismatch for new flag: expected "%s", found "%s"' % (flag_hash, response.text))
            exit(exit_code)

    except ConnectionError as error:
        print_to_stderr("Connection error: hostname: {}, error: {}".format(hostname, error))
        exit_code = DOWN
    except HTTPError as error:
        print_to_stderr("HTTP Error: hostname: {}, error: {}".format(hostname, error))
        exit_code = MUMBLE
    if exit_code == OK:
        print(name)
    exit(exit_code)


def get(hostname, flag_id, flag, _):

    name = flag_id
    flag_hash = hash_flag(flag)

    exit_code = OK
    try:
        response = requests.get('http://%s:4280/mix?name=%s' % (hostname, name))
        response.raise_for_status()

        if flag_hash != response.text:
            exit_code = CORRUPT
            print_to_stderr('Hash mismatch for new flag: expected "%s", found "%s"' % (flag_hash, response.text))
            exit(exit_code)

    except ConnectionError as error:
        print_to_stderr("Connection error: hostname: {}, error: {}".format(hostname, error))
        exit_code = DOWN
    except HTTPError as error:
        print_to_stderr("HTTP Error: hostname: {}, error: {}".format(hostname, error))
        exit_code = MUMBLE
    if exit_code == OK:
        print(name)
    exit(exit_code)


def make_recipe_for_name(name):
    flag = name + '0' * (31 - len(name)) + '='
    return ','.join(flag_to_recipe(flag))

#print(make_recipe_for_name(input()))

print(flag_to_recipe('1AG359TGGAGG7AKT5XTIO8KHZ1J4VMW='))
