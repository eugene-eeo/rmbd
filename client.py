import struct
import socket
from rmbd.protocol import bit, Type, ADD_REQ, COUNT_REQ, SYNC_REQ, COUNT_RES, PEER_REQ


class RmbdClient:
    def __init__(self, addr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = addr

    def send(self, req):
        self.socket.sendto(req, self.addr)

    def add(self, key):
        self.send(bit(Type.add) + ADD_REQ.pack(key))

    def count(self, key):
        self.send(bit(Type.count) + COUNT_REQ.pack(key))
        recv, count = COUNT_RES.unpack(self.socket.recv(COUNT_RES.size))
        if recv == key:
            return count

    def sync(self, row, counters):
        self.send(bit(Type.sync) + SYNC_REQ.pack(row, *counters))

    def peer(self, peer):
        self.send(bit(Type.peer) + PEER_REQ.pack(*peer))
