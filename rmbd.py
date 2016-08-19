from collections import deque
from struct import Struct
from fnvhash import fnv1a_32
from gevent.server import DatagramServer
import gevent.socket as socket
import gevent


def khash(k, datum):
    for i in range(k):
        yield fnv1a_32(datum, i)


class CountMinSketch:
    def __init__(self, width, depth):
        self.width = width
        self.depth = depth
        self.array = [[0]*self.width for _ in range(self.depth)]

    def add(self, datum):
        for row, h in zip(self.array, khash(self.depth, datum)):
            row[h % self.width] += 1

    def count(self, datum):
        xs = []
        for row, h in zip(self.array, khash(self.depth, datum)):
            xs.append(row[h % self.width])
        return min(xs)


def merge(cms, index, counters):
    row = cms.array[index]
    for idx, item in enumerate(counters):
        row[idx] = max(row[idx], item)


DEPTH = 10
WIDTH = 100
KEY   = Struct('140p')
INDEX = Struct('H')
COUNT = Struct('L')

COUNT_RES = Struct(KEY.format + COUNT.format)
PEER_REQ  = Struct(KEY.format + COUNT.format)
SYNC_REQ  = Struct(INDEX.format + COUNT.format * WIDTH)

MAX_PEERS  = 10
SYNC_DELAY = 0.5


def background_sync(cms, peers):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        gevent.sleep(SYNC_DELAY)
        to_remove = []
        for peer in peers:
            try:
                for index, counters in enumerate(cms.array):
                    sock.sendto(
                        chr(2).encode() + SYNC_REQ.pack(index, *counters),
                        peer,
                        )
            except ConnectionError:
                to_remove.append(peer)
        for peer in to_remove:
            peers.remove(peer)


class RMBServer(DatagramServer):
    def start(self):
        super().start()
        self.peers = deque(maxlen=MAX_PEERS)
        self.cms = CountMinSketch(
            width=WIDTH,
            depth=DEPTH,
            )
        self.bg = gevent.spawn(background_sync, self.cms, self.peers)

    def close(self):
        self.bg.kill()
        super().close()

    def handle(self, data, address):
        type = data[0]
        rest = memoryview(data)[1:]

        # add request
        if type == 0:
            key, = KEY.unpack(rest)
            print('ADD %r from %s' % (key, address))
            self.cms.add(key)

        # count request
        elif type == 1:
            key, = KEY.unpack(rest)
            print('COUNT %r from %s' % (key, address))
            self.socket.sendto(
                COUNT_RES.pack(key, self.cms.count(key)),
                address,
                )

        # sync request
        elif type == 2:
            index, *counters = SYNC_REQ.unpack(rest)
            print('SYNC %r from %s' % (index, address))
            merge(self.cms, index, counters)

        # peer request
        elif type == 3:
            addr, port = PEER_REQ.unpack(rest)
            print('PEER %r from %s' % ((addr, port), address))
            self.peers.append((addr, port))


if __name__ == '__main__':
    import sys
    RMBServer(sys.argv[1]).serve_forever()
