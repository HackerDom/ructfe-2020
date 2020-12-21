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


def get_flight_state_bytes(token: str,
                           x: int, y: int, flight_id: bytes,
                           label: str, license: str, finished: bool) -> bytes:
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


def parse_token(set_cookie_value: str) -> str:
    return set_cookie_value[len("token="):-len("; expires=Thu, 24 Dec 2020 20:15:05 GMT; path=/")]

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

        """
        __RequestVerificationToken: CfDJ8A6N6emswSRMktHB7R3eAIvCd_VIoOZPoNH87-efpUyBqsCUeNMaxP2AuyARCqp4qGk0eNwYW1KeZpWEYjmjOAN0dLKFr2mbIN2qeWM3F_jQ7fQLao3lZrxeFPlIfppA3v34a2WVjithEB8V6iv5BPY
        """
        res = s.post(f'{self.http_address}/LoginOrRegister?handler=Register',
                     headers={'Content-Type': 'application/x-www-form-urlencoded'},
                     data="__RequestVerificationToken=CfDJ8A6N6emswSRMktHB7R3eAIvCd_VIoOZPoNH87-efpUyBqsCUeNMaxP2AuyARCqp4qGk0eNwYW1KeZpWEYjmjOAN0dLKFr2mbIN2qeWM3F_jQ7fQLao3lZrxeFPlIfppA3v34a2WVjithEB8V6iv5BPY"
                          f"&userName={login}"
                          f"&company={company}"
                          f"&password={password}",
                     allow_redirects=False)

        if res.status_code != 302:
            print('[-] Registration fail')
            return None
        print('[+] Registration success')
        token = parse_token(res.headers.get("Set-Cookie"))
        return token

    def login_and_get_auth_token(self, login, password):
        s = Session()

        res = s.post(f'{self.http_address}/LoginOrRegister?handler=Login',
                     headers={'Content-Type': 'application/x-www-form-urlencoded'},
                     data="__EVENTTARGET="
                          f"&userName={login}"
                          f"&password={password}",
                     allow_redirects=False)

        if res.status_code != 302:
            print('[-] Login fail')
            return None
        print('[+] Login success')
        token = parse_token(res.headers.get("Set-Cookie"))
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
