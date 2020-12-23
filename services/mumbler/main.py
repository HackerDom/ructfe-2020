from req_handers import ThreadedUDPServer, ThreadedUDPRequestHandler
from flask import Flask, make_response
import storage as s
import uuid
import threading

app = Flask(__name__)
storage = s.Storage()


def run_udp_listener(*args):
    server = ThreadedUDPServer((args[0], args[1]), ThreadedUDPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True

    try:
        server_thread.start()
        print "Server started at {} port {}".format(*args)
    except (KeyboardInterrupt, SystemExit) as e:
        print e
        server.shutdown()
        server.server_close()


@app.route(u"/data/<key>")
def get_data(key):
    try:
        data = uuid.UUID(key)
        return make_response(storage.read(data).strip()[:50], 200)
    except:
        return make_response("something happened", 400)


if __name__ == '__main__':
    run_udp_listener(u"0.0.0.0", 7125)
    app.run(u"0.0.0.0", 7124)
