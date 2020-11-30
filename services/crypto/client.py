from sys import argv
import json
import urllib.request

host = "localhost:3113"

def get_token(login, password):
    newConditions = {"addition": {"login": login, "password":password}}
    req = urllib.request.Request("http://"+host+"/get_token", data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]["token"]


def register(login, password, credit_card_credentials, public_key_base64):
    newConditions = {"addition": {"login": login, "password":password, "credit_card_credentials":credit_card_credentials, "public_key_base64":public_key_base64}}
    req = urllib.request.Request("http://"+host+"/register", data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def send_money(token, to, amount, description):
    newConditions = {"addition": {"token":token, "to":to, "amount":amount, "description":description}}
    req = urllib.request.Request("http://"+host+"/send_money",
                                    data=json.dumps(newConditions).encode('utf-8'),
                                    headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_users():
    req = urllib.request.Request("http://"+host+"/users_pubkeys", 
                                headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_user_by_token(token):
    newConditions = {"addition": {"token": token}}
    req = urllib.request.Request("http://"+host+"/get_user", data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_user_by_login_and_password(login, password):
    token = get_token(login, password)
    return get_user_by_token(token)
a=get_user_by_login_and_password("6","2")
print(a)