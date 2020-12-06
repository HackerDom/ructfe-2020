#!/usr/bin/env python3.8
from requests import Session
from string import ascii_lowercase
from random import choices, randint
from urllib.parse import urlparse, parse_qs
from base64 import urlsafe_b64encode
from hashlib import sha256
from re import match, compile
import json
import urllib.request
import socket
import base64


def gen_random_string(k=10):
    return ''.join(choices(ascii_lowercase, k=k))


def get_creds():
    return gen_random_string, gen_random_string(), gen_random_string()


def get_coordinates_bytes(token: str, x: int, y: int):
    with open("coords_example.bin", 'rb') as f:
        template = f.readline()
    template = template.replace(b'xxxx', int.to_bytes(x, 4, 'little'))
    template = template.replace(b'yyyy', int.to_bytes(y, 4, 'little'))
    template = template.replace(b'tttttttttttttttttttttttttttttttt', token.encode('ascii'))
    return template




class Client:
    def __init__(self, ip_address, tcp_port, http_port):
        self.http_address = f"http://{ip_address}:{http_port}"
        self.ip_address = ip_address
        self.tcp_port = tcp_port
        self.http_port = http_port

    def send_coordinates(self, token, x: int, y: int):
        data = get_coordinates_bytes(token, x, y)
        return self.send_bytes(data)

    def send_bytes(self, data: bytes):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip_address, self.tcp_port))
        s.sendall(data)
        result = s.recv(1024 * 100)
        return result

    def send_base64(self, base64_str: str):
        data = base64.b64decode(base64_str)
        return self.send_bytes(data)

    def get_auth_token(self):
        s = Session()
        login, company, password = get_creds()
        login = "23456s33r"
        company = "3333333"
        password = "e4rty"
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
        print('[+] Registration compile')
        token = res.headers.get("Set-Cookie")[6:-8]  # token={xxx}; path=/
        return token


host = ""
def get_token(login, password):
    newConditions = {"addition": {"login": login, "password": password}}
    req = urllib.request.Request("http://" + host + "/get_token", data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]["token"]


def register(login, password, credit_card_credentials, public_key_base64):
    newConditions = {
        "addition": {"login": login, "password": password, "credit_card_credentials": credit_card_credentials,
                     "public_key_base64": public_key_base64}}
    req = urllib.request.Request("http://" + host + "/register", data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]


def send_money(token, to, amount, description):
    newConditions = {"addition": {"token": token, "to": to, "amount": amount, "description": description}}
    req = urllib.request.Request("http://" + host + "/send_money",
                                 data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]


def get_users():
    req = urllib.request.Request("http://" + host + "/users_pubkeys",
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]


def get_user_by_token(token):
    newConditions = {"addition": {"token": token}}
    req = urllib.request.Request("http://" + host + "/get_user", data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]


def get_user_by_login_and_password(login, password):
    token = get_token(login, password)
    return get_user_by_token(token)
