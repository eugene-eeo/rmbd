from collections import deque
from time import time
from .countminsketch import CountMinSketch, merge
from .protocol import parse, COUNT_RES, SYNC_REQ, Type, WIDTH, DEPTH
from gevent.server import DatagramServer
import gevent.socket as socket
import gevent


class RMBServer(DatagramServer):
    def start(self):
        super().start()
        self.peers = set()
        self.cms = CountMinSketch(
            width=WIDTH,
            depth=DEPTH,
            )
        self.acks = {}
        self.closing = False
        self.bg_sync = gevent.spawn(self.background_sync)
        self.handlers = {
            Type.add:   self.handle_add,
            Type.count: self.handle_count,
            Type.sync:  self.handle_sync,
            Type.peer:  self.handle_peer,
            Type.ack:   self.handle_ack,
        }

    def handle(self, data, address):
        request = parse(memoryview(data), address)
        if request:
            self.handlers[request.type](request)

    def background_sync(self, delay=0.5):
        times = {}
        while not self.closing:
            for peer in times:
                ack = self.acks.get(peer, 0)
                if ack < times[peer]:
                    self.peers.remove(peer)
            times.clear()

            for index, row in enumerate(self.cms.array):
                packet = chr(Type.sync.value).encode() + SYNC_REQ.pack(index, *row)
                for peer in self.peers:
                    self.socket.sendto(packet, peer)
                    times[peer] = time()
            gevent.sleep(delay)

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
            self.socket.sendto(chr(Type.ack.value).encode(), request.peer)

    def handle_peer(self, request):
        addr, port = request.params
        self.peers.add((socket.gethostbyname(addr), port))

    def handle_ack(self, request):
        self.acks[request.peer] = time()

    def close(self):
        self.closing = True
        super().close()
