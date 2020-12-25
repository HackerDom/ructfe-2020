#!/usr/bin/env python3

import requests
import traceback
import random
import string
import time

from bs4 import BeautifulSoup
from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest
from gornilo.models.verdict.verdict_codes import *

checker = Checker()


@checker.define_check
def check_service(request: CheckRequest) -> Verdict:
    rand_key = ''.join(random.choice(string.ascii_uppercase) for _ in range(32))
    url = "http://" + request.hostname + ":4280/" + rand_key
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")
        key = soup.find(id="key").text
        if key == rand_key:
            return Verdict.OK()
        print("Expected to find random key " + rand_key + "on the page, but found " + key)
        return Verdict.MUMBLE("Front page is broken!")
    except:
        traceback.print_exc()
        return Verdict.MUMBLE("Couldn't get a meaningful response!")


@checker.define_put(vuln_num=1, vuln_rate=1)
def put_flag(request: PutRequest) -> Verdict:
    url = "http://" + request.hostname + ":4280/"
    try:
        for i in range(3):
            response = requests.post(url, data = { "secret": request.flag[:31] }, allow_redirects = False)
            key = response.headers['Location'][1:]
            if len(key) == 0:
                print("Couldn't get flag id. Response was: ", vars(response))
                time.sleep(i + 1)
                continue
            print("Saved flag " + request.flag)
            return Verdict.OK(key)
        return Verdict.MUMBLE("Couldn't put flag!")
    except:
        traceback.print_exc()
        return Verdict.MUMBLE("Couldn't get a meaningful response!")


@checker.define_get(vuln_num=1)
def get_flag(request: GetRequest) -> Verdict:
    url = "http://" + request.hostname + ":4280/" + request.flag_id.strip()
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")
        secret = soup.find(id="secret").text
        if secret + "=" == request.flag:
            return Verdict.OK()
        if secret == '':
            print("Flag is missing for id = " + request.flag_id)
            return Verdict.CORRUPT("Flag is missing!")
        print("Flag value mismatch for id = " + request.flag_id + ". Got " + secret +
            ", wanted " + request.flag)
        return Verdict.CORRUPT("Flag value mismatch!")
    except:
        traceback.print_exc()
        return Verdict.MUMBLE("Couldn't get a meaningful response!")



if __name__ == '__main__':
    checker.run()
