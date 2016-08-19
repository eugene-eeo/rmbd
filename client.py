import struct
import socket
from rmbd.protocol import KEY, SYNC_REQ, COUNT_RES, PEER_REQ

b = lambda x: chr(x).encode()


class RmbdClient:
    def __init__(self, addr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = addr

    def send(self, req):
        self.socket.sendto(req, self.addr)

    def add(self, key):
        self.send(b(0) + KEY.pack(key))

    def count(self, key):
        self.send(b(1) + KEY.pack(key))
        recv, count = COUNT_RES.unpack(self.socket.recv(COUNT_RES.size))
        if recv == key:
            return count

    def sync(self, row, counters):
        self.send(b(2) + SYNC_REQ.pack(row, *counters))

    def peer(self, peer):
        self.send(b(3) + PEER_REQ.pack(*peer))
