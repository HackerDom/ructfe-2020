#!/usr/bin/env python3.8
from requests import Session
from string import ascii_lowercase
import random
from urllib.parse import urlparse, parse_qs
from base64 import urlsafe_b64encode
from hashlib import sha256
from re import match, compile
import json
import urllib.request
import socket
import base64


def get_flight_state_bytes(token: str, x: int, y: int, flight_id: bytes, label: str, license: str, finished: bool):
    if len(flight_id) != 16 or len(label) != 15 or len(token) != 32 or len(license) != 32:
        raise ValueError("Check parameters!!!")

    with open("flight_state_example.bin", 'rb') as f:
        template = f.readline()

    template = template.replace(b'{STRING_32_SYMBOLS_TOKEN}', token.encode('ascii'))
    template = template.replace(b'{INT_X}', int.to_bytes(x, 4, 'little'))
    template = template.replace(b'{INT_Y}', int.to_bytes(y, 4, 'little'))
    template = template.replace(b'{GUID_16_BYTES_FLIGHT_ID}', flight_id)
    template = template.replace(b'{STRING_15_SYMBOLS_LABEL}', label.encode('ascii'))
    template = template.replace(b'{STRING_32_SYMBOLS_LICENSE}', license.encode('ascii'))
    template = template.replace(b'{BOOL_FINISHED}', b'\xff' if finished else b'\0')
    return template


class Client:
    def __init__(self, ip_address, tcp_port, http_port):
        self.ip_address = ip_address
        self.tcp_port = tcp_port
        self.http_port = http_port
        self.http_address = f"http://{ip_address}:{http_port}"

    def send_flight_state(self, token, x: int, y: int, flight_id: bytes, label: str, license: str, finished: bool):
        data = get_flight_state_bytes(token, x, y, flight_id, label, license, finished)
        return self.send_bytes(data)

    def register_and_get_auth_token(self, login, password):
        s = Session()
        company = random.choice(companies)

        res = s.post(f'{self.http_address}/Register',
                     headers={'Content-Type': 'application/x-www-form-urlencoded'},
                     data="__EVENTTARGET="
                          "&__EVENTARGUMENT="
                          "&__VIEWSTATE=SJWnsBq%2BPUcp2FjFO1eknNTAuwgavy%2BQjf0glWUxkKf8Brhnh3xoum%2BZarTys%2BMYeL%2Bbl9AfKIasMO%2FMx0SmESO6lACptCu0lYHL4L4jSj0JjpIRQyfWyKtq2fGd0HTpYo%2F0eiCY0v317MKzKfDK%2Bmu31u5S1fYJXOn0xuafM6grPFAYkrptpPqToTfoTApt"
                          "&__VIEWSTATEGENERATOR=799CC77D"
                          "&__EVENTVALIDATION=tpqY7OKHM0Xn9Cp1S5URkGxLyQ9CVxV00ivj3cODkk1%2FxGw2h2nVTdkB0ebV7CUgW9GD%2BKrcdvc6Mf2AMUJE6bPc%2FS5qg7h1PGlPwUuR8VSL4Adscr9%2BJC9%2B6nd2W9GH5hTDE2t6TMU0AC%2Fu9Mvc8hsvfrWarZBqkOoESrq6Wyr5XaoqnB38a1m4Et7liJCfdQaF0DR51W3ZZWTClKtDoQ%3D%3D"
                          f"&ctl00$MainContent$txtUserName={login}"
                          f"&ctl00$MainContent$txtCompanyName={company}"
                          f"&ctl00$MainContent$txtUserPass={password}"
                          f"&ctl00$MainContent$cmdRegister=Register",
                     allow_redirects=False)

        if res.status_code != 302:
            print('[-] Registration fail')
            return None
        print('[+] Registration success')
        token = res.headers.get("Set-Cookie")[6:-8]  # "token={xxx}; path=/"
        return token

    def login_and_get_auth_token(self, login, password):
        s = Session()

        res = s.post(f'{self.http_address}/Login',
                     headers={'Content-Type': 'application/x-www-form-urlencoded'},
                     data="__EVENTTARGET="
                          "&__EVENTARGUMENT="
                          "&__VIEWSTATE=FnsS5VBdXN36voLmK%2FvWGRTS4zwdkeC7kGu8KWz9Ws37a2mValPuwUW%2F%2BiKJzBmgrxorH3g3zP418B4h%2Frn4LyEJDcWT7%2Be2YcKbc8nQgl1MLF3B6QRaujaRFEuxH9clRtJXz%2FdF4jkRWT2FNWLHEgyZn3L6zTYaPdZSjStTO8u%2BtU%2BCDpf88DvczOeFXZmU"
                          "&__VIEWSTATEGENERATOR=C2EE9ABB"
                          "&__EVENTVALIDATION=ay%2FsBoDqoTzxCeKME4oa6Fxc%2FPZd1EX%2BlvXU0yAVm1TeEWWbBdJGV2AG%2BB9qiGkVC4gx%2FPnPqU5MnyZVXbU1gHs5%2ByzNz1Jztiu7qwOeLNbKWi%2BtGO8Wzk9C%2FOXkQL1mfRV4gW2TMEmO79wTnIr47FkWgrc%2BzbDRp%2FN8nM4is%2F9%2BBRXOGA5NIqqGWyFv4SDk"
                          f"&ctl00$MainContent$txtUserName={login}"
                          f"&ctl00$MainContent$txtUserPass={password}"
                          f"&ctl00$MainContent$cmdLogin=Login",
                     allow_redirects=False)

        if res.status_code != 302:
            print('[-] Login fail')
            return None
        print('[+] Login success')
        token = res.headers.get("Set-Cookie")[6:-8]  # "token={xxx}; path=/"
        return token

    def send_bytes(self, data: bytes):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip_address, self.tcp_port))
        s.sendall(data)
        result = s.recv(1024 * 100)
        return result

    def send_base64(self, base64_str: str):
        data = base64.b64decode(base64_str)
        return self.send_bytes(data)


companies = [
    # https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%90%D0%B2%D0%B8%D0%B0%D0%BA%D0%BE%D0%BC%D0%BF%D0%B0%D0%BD%D0%B8%D0%B8_%D0%BF%D0%BE_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B0%D0%BC
    "Ural Airlines",
    "Pobeda",
    "Flydubai",
    "Etihad Airways",
    "Emirates",
    "Air Arabia",
]
