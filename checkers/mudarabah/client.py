from sys import argv
import json
import urllib.request

PORT = 3113

def ping(host):
    req = urllib.request.Request(f"http://{host}:{PORT}/ping")
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))

def get_cookie(host, login, password):
    newConditions = {"addition": {"login": login, "password":password}}
    req = urllib.request.Request(f"http://{host}:{PORT}/get_cookie", data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]["cookie"]


def register(host, login, password, credit_card_credentials):
    newConditions = {"addition": {"login": login, "password":password, "credit_card_credentials":credit_card_credentials}}
    req = urllib.request.Request(f"http://{host}:{PORT}/register", data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def send_money(host, cookie, login_to, amount, description):
    newConditions = {"addition": {"cookie":cookie, "login_to":login_to, "amount":amount, "description":description}}
    req = urllib.request.Request(f"http://{host}:{PORT}/send_money",
                                    data=json.dumps(newConditions).encode('utf-8'),
                                    headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))

def get_transactions(host, login):
    newConditions = {"addition": {"login":login}}
    req = urllib.request.Request(f"http://{host}:{PORT}/transactions",
                                    data=json.dumps(newConditions).encode('utf-8'),
                                    headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))
