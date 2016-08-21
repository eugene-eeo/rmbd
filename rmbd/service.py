from collections import defaultdict
from time import time
import gevent
import gevent.socket as socket
from .countminsketch import CountMinSketch, merge
from .protocol import parse, COUNT_RES, SYNC_REQ, Type, WIDTH, DEPTH, bit, Request


def sum_cms_count(key, table):
    return sum(cms.count(key) for cms in table.values())


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
        self.cms = CountMinSketch(width=WIDTH, depth=DEPTH)
        self.peer_cms = defaultdict(CountMinSketch)
        self.address = normalize(address)
        self.socket = socket
        self.peers = set()
        self.acks = {}
        self.stopped = False
        self.bg_sync = gevent.spawn(self.background_sync)
        self.handlers = {
            Type.add:   self.handle_add,
            Type.count: self.handle_count,
            Type.sync:  self.handle_sync,
            Type.peer:  self.handle_peer,
            Type.ack:   self.handle_ack,
            }

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
            for index, row in enumerate(self.cms.array):
                packet = bit(Type.sync) + SYNC_REQ.pack(index, *row)
                for peer in self.peers:
                    self.socket.sendto(packet, peer)
                    last_sent[peer] = time()
            gevent.sleep(self.sync_delay)

    def handle_add(self, request):
        key, = request.params
        self.cms.add(key)

    def handle_count(self, request):
        key, = request.params
        count = self.cms.count(key) + sum_cms_count(key, self.peer_cms)
        self.socket.sendto(
            COUNT_RES.pack(key, count),
            request.peer,
            )

    def handle_sync(self, request):
        index, *row = request.params
        cms = self.peer_cms[request.peer]
        if index < cms.depth:
            merge(cms, index, row)
            self.socket.sendto(bit(Type.ack), request.peer)

    def handle_peer(self, request):
        peer = normalize(request.params)
        if peer != self.address:
            self.peers.add(peer)

    def handle_ack(self, request):
        self.acks[request.peer] = time()
