import SocketServer
import threading


class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        current_thread = threading.current_thread()
        print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))


class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    def get_request(self):
        print u"shit is happening"
        arr = bytearray()
        nbytes, client_addr = self.socket.recvfrom_into(arr, self.max_packet_size)
        return (arr, self.socket), client_addr
