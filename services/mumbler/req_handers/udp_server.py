from storage import Storage

import re
import uuid
import time
import socket
import threading
import sys

allowed_key_name = re.compile(r"^[A-Za-z0-9=-]{1,60}$")


class UDPReceiver:
    udp_max_size = 8192

    def __init__(self):
        self.max_ports_size = 1000
        self.listeners = dict()
        self.lock = threading.Lock()
        threading.Thread(target=self.log_status).start()

    def log_status(self):
        while True:
            time.sleep(5)
            print >> sys.stderr, "Available udp ports: {}"\
                .format(self.max_ports_size - len(self.listeners))
            print >> sys.stderr, "Amount of working threads: {}"\
                .format(threading.active_count())

    def add_listener(self, buf_size, port):
        with self.lock:
            if len(self.listeners) >= self.max_ports_size:
                raise ValueError("too much listeners")
            lst_id = uuid.uuid4()
            t = threading.Thread(target=self.__create_listener, args=(port, lst_id, buf_size))
            self.listeners[lst_id] = t
            t.start()

    def __create_listener(self, port, lst_id, buf_size):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", port))
            print >> sys.stderr, "opened socket at {}".format(port)
            arr = bytearray(min(self.udp_max_size, buf_size))
            _, __ = sock.recvfrom_into(arr, self.udp_max_size)
            self.__handle(arr)
        finally:
            print >> sys.stderr, "closed socket at {}".format(port)
            with self.lock:
                del self.listeners[lst_id]

    def __handle(self, data):
        data = data.strip()
        try:
            result = data.split(":")
            if len(result) != 2:
                raise
            store = Storage()
            uuid.UUID(result[0].decode())
            if not re.match(allowed_key_name, result[1].decode().strip("\x00")):
                raise
            store.write(result[0], result[1])
            print >> sys.stderr, "handled data"
        except:
            pass
