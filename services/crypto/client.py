from sys import argv
import json
import urllib.request

host = "localhost:3113"

def get_status_dict(uuid_str):
    newConditions = {"addition": {"uuid": uuid_str}}
    req = urllib.request.Request("http://"+host+"/api/status", data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]

def get_subs_json_bytes():
    response = urllib.request.urlopen("http://"+host+"/api/subs")
    return response.read()

def get_token(login, password):
    newConditions = {"addition": {"login": login, "password":password}}
    req = urllib.request.Request("http://"+host+"/get_token", data=json.dumps(newConditions).encode('utf-8'),
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))["addition"]


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

#register("1","2","3","4")
token = get_token("1", "2")["addition"]["token"]
send_money(token, "5", 10, "aaaa")