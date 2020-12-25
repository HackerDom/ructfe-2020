from storage import Storage

import re
import uuid
import time
import socket
import threading
import multiprocessing
import sys

allowed_key_name = re.compile(r"^[A-Za-z0-9=-]{1,60}$")


class UDPReceiver:
    udp_max_size = 8192

    def __init__(self):
        self.max_ports_size = 12000
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

    def add_listener(self, data):
        with self.lock:
            if len(self.listeners) >= self.max_ports_size:
                raise ValueError("too much listeners")
            lst_id = uuid.uuid4()

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", 0))
            current_port = sock.getsockname()[1]

            print >> sys.stderr, "opened socket at {}".format(current_port)

            t = threading.Thread(target=self.__create_listener, args=(sock, current_port, lst_id, data))
            self.listeners[lst_id] = t
            t.start()
            return current_port

    def __create_listener(self, sock, port, lst_id, ds):
        try:
            arr = bytearray(min(self.udp_max_size, ds))
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
