from time import time
import gevent
import gevent.socket as socket
from .bloomfilter import BloomFilter, merge, partition
from .protocol import parse, HAS_RES, SYNC_REQ, Type, bit, Request


def normalize(addr):
    host, port = addr
    return socket.gethostbyname(host), port


def get_outdated(acks, last_sent):
    for peer in last_sent:
        if acks.get(peer, 0) < last_sent[peer]:
            yield peer


class Service(object):
    sync_delay = 0.5

    def __init__(self, address, socket):
        self.bf = BloomFilter()
        self.address = normalize(address)
        self.socket = socket
        self.peers = set()
        self.acks = {}
        self.stopped = False
        self.handlers = {
            Type.add:  self.handle_add,
            Type.has:  self.handle_has,
            Type.sync: self.handle_sync,
            Type.peer: self.handle_peer,
            Type.ack:  self.handle_ack,
            }
        gevent.spawn(self.background_sync)

    def dispatch(self, data, addr):
        info = parse(data)
        if not info:
            return
        req = Request(*info, addr)
        self.handlers[req.type](req)

    def stop(self):
        self.stopped = True

    def background_sync(self):
        last_sent = {}
        while not self.stopped:
            for peer in get_outdated(self.acks, last_sent):
                self.peers.remove(peer)
            self.acks.clear()
            last_sent.clear()
            if self.peers:
                for offset, row in partition(self.bf):
                    packet = bit(Type.sync) + SYNC_REQ.pack(offset, *row)
                    for peer in self.peers:
                        self.socket.sendto(packet, peer)
                        last_sent[peer] = time()
            gevent.sleep(self.sync_delay)

    def handle_add(self, request):
        key, = request.params
        self.bf.add(key)

    def handle_has(self, request):
        key, = request.params
        self.socket.sendto(
            HAS_RES.pack(key, self.bf.has(key)),
            request.peer,
            )

    def handle_sync(self, request):
        offset, *row = request.params
        if offset < self.bf.depth:
            merge(self.bf, offset, row)
            self.socket.sendto(bit(Type.ack), request.peer)

    def handle_peer(self, request):
        peer = normalize(request.params)
        if peer != self.address:
            self.peers.add(peer)

    def handle_ack(self, request):
        self.acks[request.peer] = time()
