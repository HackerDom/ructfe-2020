# -*- coding: utf-8 -*-
from req_handers import UDPReceiver
from flask import Flask, make_response
import storage as s
import uuid
import random
import os
import threading
import time
from hashlib import sha1

app = Flask(__name__)
storage = s.Storage()
udp = UDPReceiver()
hashed = ""

with open("index.html", mode="rb") as i:
    INDEX = i.read().decode("utf-8")


def updater():
    def __update_index():
        global hashed
        while True:
            try:
                dir_files = os.listdir("storage")
                hashed = str(sha1(str(dir_files).encode()).hexdigest())[:31].upper() + "= "
            finally:
                time.sleep(50)
    threading.Thread(target=__update_index).start()


updater()


@app.route("/")
def index():
    response = INDEX\
        .replace("#", "")\
        .replace(u"&", u"    ...شخص ما تمتم لي بعض الأشياء ")\
        .replace("?", ".")
    return make_response(response, 200)


@app.route("/mumble")
def mumble():
    response = INDEX.replace("#", "").replace("&", hashed).replace("?", "@")
    return make_response(response, 200)


@app.route("/data/<key>")
def get_data(key):
    try:
        data = uuid.UUID(key)
        return make_response(storage.read(data).strip()[:50], 200)
    except:
        return make_response("something happened", 400)


@app.route("/open/<size>")
def open_receiver(size):
    try:
        port = random.randint(0, 1000) + 30000
        udp.add_listener(abs(int(size)), port)
        return make_response(str(port), 200)
    except:
        return make_response("something bad happened", 500)


if __name__ == '__main__':
    app.run(u"0.0.0.0", 7124, threaded=True)
