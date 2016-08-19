from collections import deque
from .countminsketch import CountMinSketch, merge
from .protocol import parse_request, COUNT_RES, SYNC_REQ, Type, WIDTH, DEPTH
from gevent.server import DatagramServer
from gevent.socket import socket
import gevent


class RMBServer(DatagramServer):
    def start(self):
        super().start()
        self.peers = deque(maxlen=10)
        self.cms = CountMinSketch(
            width=WIDTH,
            depth=DEPTH,
            )
        self.bg_sync = gevent.spawn(self.background_sync)
        self.handlers = {
            Type.add:   self.handle_add,
            Type.count: self.handle_count,
            Type.sync:  self.handle_sync,
            Type.peer:  self.handle_peer,
        }

    def handle(self, data, address):
        request = parse_request(memoryview(data))
        if request:
            self.handlers[request.type](request.params, address)

    def background_sync(self, delay=0.5):
        while True:
            gevent.sleep(delay)
            for index, row in enumerate(self.cms.array):
                to_remove = set()
                packet = chr(Type.sync.value).encode() + SYNC_REQ.pack(index, *row)
                for peer in self.peers:
                    try:
                        self.socket.sendto(packet, peer)
                    except ConnectionError:
                        print('DISCONNECTING %r' % peer)
                        to_remove.add(peer)

                for peer in to_remove:
                    self.peers.discard(peer)

    def handle_add(self, params, address):
        key, = params
        self.cms.add(key)

    def handle_count(self, params, address):
        key, = params
        self.socket.sendto(COUNT_RES.pack(key, self.cms.count(key)), address)

    def handle_sync(self, params, address):
        index, *row = params
        if index < self.cms.depth:
            merge(self.cms, index, row)

    def handle_peer(self, params, address):
        addr, port = params
        self.peers.append((addr, port))
