from req_handers import UDPReceiver
from flask import Flask, make_response
import storage as s
import uuid
import random

app = Flask(__name__)
storage = s.Storage()
udp = UDPReceiver()


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
    app.run(u"0.0.0.0", 7124)
