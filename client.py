import struct
import socket


class RmbdClient:
    def __init__(self, addr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = addr

    def send(self, req):
        self.socket.sendto(req, self.addr)

    def add(self, key):
        self.send(b'0' + key)

    def count(self, key):
        self.send(b'1' + key)
        size = struct.calcsize('L140p')
        count, recv = struct.unpack('L140p', self.socket.recv(size))
        if recv == key:
            return count

    def sync(self, row, counters):
        self.send(b'2' + struct.pack(
            'H' + 'L'*len(counters),
            *((row,) + tuple(counters)))
            )
