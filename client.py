import struct
import socket
from rmbd.protocol import bit, Type, ADD_REQ, HAS_REQ, SYNC_REQ, \
    PEER_REQ, HAS_RES


class RmbdClient:
    def __init__(self, addr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = addr

    def request(self, reqtype, format, *params):
        self.socket.sendto(bit(reqtype) + format.pack(*params), self.addr)

    def add(self, key):
        self.request(Type.add, ADD_REQ, key)

    def has(self, key):
        self.request(Type.has, HAS_REQ, key)
        recv, exists = HAS_RES.unpack(self.socket.recv(HAS_RES.size))
        if recv == key:
            return exists

    def sync(self, row, counters):
        self.request(Type.sync, SYNC_REQ, row, *counters)

    def peer(self, peer):
        self.request(Type.peer, PEER_REQ, *peer)
