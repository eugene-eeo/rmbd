from time import time
from .countminsketch import CountMinSketch, merge
from .protocol import parse, COUNT_RES, SYNC_REQ, Type, WIDTH, DEPTH, bit
from .helpers import get_outdated, broadcast, normalize
import gevent


class Service(object):
    sync_delay = 0.5

    def __init__(self, address, socket):
        self.cms = CountMinSketch(width=WIDTH, depth=DEPTH)
        self.address = normalize(address)
        self.socket = socket
        self.peers = set()
        self.acks = {}
        self.bg_sync = gevent.spawn(self.background_sync)
        self.handlers = {
            Type.add:   self.handle_add,
            Type.count: self.handle_count,
            Type.sync:  self.handle_sync,
            Type.peer:  self.handle_peer,
            Type.ack:   self.handle_ack,
            }

    def dispatch(self, data, addr):
        req = parse(data, addr)
        if req:
            self.handlers[req.type](req)

    def stop(self):
        self.bg_sync.kill()

    def background_sync(self):
        last_sent = {}
        while True:
            for peer in get_outdated(self.acks, last_sent):
                self.peers.remove(peer)
            self.acks.clear()
            last_sent.clear()
            for index, row in enumerate(self.cms.array):
                last_sent.update(broadcast(
                    self.socket,
                    self.peers,
                    bit(Type.sync) + SYNC_REQ.pack(index, *row),
                    ))
            gevent.sleep(self.sync_delay)

    def handle_add(self, request):
        key, = request.params
        self.cms.add(key)

    def handle_count(self, request):
        key, = request.params
        self.socket.sendto(
            COUNT_RES.pack(key, self.cms.count(key)),
            request.peer,
            )

    def handle_sync(self, request):
        index, *row = request.params
        if index < self.cms.depth:
            merge(self.cms, index, row)
            self.socket.sendto(bit(Type.ack), request.peer)

    def handle_peer(self, request):
        peer = normalize(request.params)
        if peer != self.address:
            self.peers.add(peer)

    def handle_ack(self, request):
        self.acks[request.peer] = time()
