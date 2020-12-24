#!/usr/bin/env python3.8
import random
import requests
import socket
import base64
import traceback
from bs4 import BeautifulSoup


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
    try:
        token = set_cookie_value[len("token="):-len("; expires=Thu, 24 Dec 2020 20:15:05 GMT; path=/")]
        print(f"[+] Token was succesfully parsed: '{str(token)}'")

        if token is None or not isinstance(token, str) or len(token) != 32:
            print("[---] Token is None or not string of 32 symbols")
            return None
        return token

    except Exception:
        print("[---] Failed to parse token from cookie")
        traceback.print_exc()
    return None


def parse_html_table(content: bytes) -> list:
    try:
        data = []
        soup = BeautifulSoup(content, features="lxml")
        table_body = soup.find('table').find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [element.text.strip() for element in cols]
            data.append([element for element in cols if element])

        print("[+] Parsed html table successfully, will try to analyze it")
        return data
    except Exception:
        print("[---] Failed to parse html table")
        traceback.print_exc()
    return None


class Client:
    def __init__(self, ip_address, tcp_port, http_port):
        self.ip_address = ip_address
        self.tcp_port = tcp_port
        self.http_port = http_port
        self.http_address = f"http://{ip_address}:{http_port}"

    def send_flight_state(self, token, x: int, y: int, flight_id: bytes, label: str, license: str, finished: bool):
        data = get_flight_state_bytes(token, x, y, flight_id, label, license, finished)
        return self.send_tcp_bytes(data)

    def get_main_page_positions(self):
        res = requests.get(self.http_address)

        if res.status_code != 200:
            print(f"[---] Get main page failed: {res.status_code}")
            return None

        print(f"[+] Get main page succeed, will try to parse its html content")
        data = parse_html_table(res.content)
        return data

    def get_chronicle(self, token):
        res = requests.get(f'{self.http_address}/Chronicle',
                           cookies={"token": token})

        if res.status_code != 200:
            print(f"[---] Get chronicle failed: {res.status_code}")
            return None

        print(f"[+] Get chronicle succeed, will try to parse its html content")
        data = parse_html_table(res.content)
        return data

    def register_and_get_auth_token(self, login, password, company):
        res = requests.post(f'{self.http_address}/LoginOrRegister?handler=Register',
                            headers={'Content-Type': 'application/x-www-form-urlencoded'},
                            data=f"&userName={login}&company={company}&password={password}",
                            allow_redirects=False)

        if res.status_code != 302:
            print(f"[---] Registration failed: expected 302, but had {res.status_code}")
            return None
        print("[+] Registration succeed")

        token = parse_token(res.headers.get("Set-Cookie"))
        return token

    def login_and_get_auth_token(self, login, password):
        res = requests.post(f'{self.http_address}/LoginOrRegister?handler=Login',
                            headers={'Content-Type': 'application/x-www-form-urlencoded'},
                            data=f"&userName={login}&password={password}",
                            allow_redirects=False)

        if res.status_code != 302:
            print(f"[---] Login failed: expected 302, but had {res.status_code}")
            return None
        print("[+] Login succeed")

        token = parse_token(res.headers.get("Set-Cookie"))
        return token

    def send_tcp_bytes(self, data: bytes):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip_address, self.tcp_port))
        s.sendall(data)
        result = s.recv(1024 * 1024)
        return result

    def send_base64(self, base64_str: str):
        data = base64.b64decode(base64_str)
        return self.send_tcp_bytes(data)
