import json
import urllib.request
from sys import argv

HOST = "http://localhost:3113"


def get_token(login, password):
    new_conditions = {"addition": {"login": login, "password":password}}
    req = urllib.request.Request(HOST+"/get_token", data=json.dumps(new_conditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]["token"]


def register(login, password, credit_card_credentials):
    new_conditions = {"addition": {"login": login, "password":password, "credit_card_credentials":credit_card_credentials}}
    req = urllib.request.Request(HOST+"/register", data=json.dumps(new_conditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def send_money(token, login_to, amount, description):
    new_conditions = {"addition": {"token":token, "login_to":login_to, "amount":amount, "description":description}}
    req = urllib.request.Request(HOST+"/send_money",
                                    data=json.dumps(new_conditions).encode('utf-8'),
                                    headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_users():
    req = urllib.request.Request(HOST+"/users_pubkeys", 
                                headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_user_by_token(token):
    new_conditions = {"addition": {"token": token}}
    req = urllib.request.Request(HOST+"/get_user", data=json.dumps(new_conditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_user_by_login_and_password(login, password):
    token = get_token(login, password)
    return get_user_by_token(token)
