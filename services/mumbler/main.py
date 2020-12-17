from req_handers import ThreadedUDPServer, ThreadedUDPRequestHandler
from flask import Flask, make_response
import time
import threading

app = Flask(__name__)


def run_udp_listener(*args):
    server = ThreadedUDPServer((args[0], args[1]), ThreadedUDPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True

    try:
        server_thread.start()
        print("Server started at {} port {}".format(*args))
    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()


@app.route(u"/")
def index():
    return make_response(u"shit", 200)


if __name__ == '__main__':
    run_udp_listener(u"0.0.0.0", 7125)
    app.run(u"0.0.0.0", 7124)