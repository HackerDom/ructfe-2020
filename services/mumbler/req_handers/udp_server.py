from storage import Storage

import re
import uuid
import SocketServer

allowed_key_name = re.compile(r"^[A-Za-z0-9=-]{1,60}$")


class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        try:
            result = data.split(":")
            if len(result) != 2:
                raise
            store = Storage()
            uuid.UUID(result[0].decode())
            if not re.match(allowed_key_name, result[1].decode().strip("\x00")):
                raise
            store.write(result[0], result[1])
        except:
            pass


class ThreadedUDPServer(SocketServer.UDPServer, SocketServer.ThreadingMixIn):
    def get_request(self):
        arr = bytearray(2 ** 7)
        _, client_addr = self.socket.recvfrom_into(arr, self.max_packet_size)
        return (arr, self.socket), client_addr
