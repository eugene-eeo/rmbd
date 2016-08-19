from collections import deque
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
        self.closing = False
        self.bg_sync = gevent.spawn(self.background_sync)
        self.handlers = {
            Type.add:   self.handle_add,
            Type.count: self.handle_count,
            Type.sync:  self.handle_sync,
            Type.peer:  self.handle_peer,
        }

    def handle(self, data, address):
        request = parse(memoryview(data), address)
        if request:
            self.handlers[request.type](request)

    def background_sync(self, delay=0.5):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not self.closing:
            gevent.sleep(delay)
            for index, row in enumerate(self.cms.array):
                to_remove = set()
                packet = chr(Type.sync.value).encode() + SYNC_REQ.pack(index, *row)
                for peer in self.peers:
                    try:
                        sock.sendto(packet, peer)
                    except ConnectionError:
                        print('DISCONNECTING %r' % peer)
                        to_remove.add(peer)

                for peer in to_remove:
                    self.peers.discard(peer)

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
        print('SYNC from %s: ROW %s' % (request.peer, index))
        if index < self.cms.depth:
            merge(self.cms, index, row)

    def handle_peer(self, request):
        self.peers.add(request.params)

    def close(self):
        self.closing = True
        super().close()
