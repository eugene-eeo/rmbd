from struct import Struct
from fnvhash import fnv1a_32
from gevent.server import DatagramServer


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
    row = cms[index]
    for idx, item in enumerate(counters):
        row[idx] = max(row[idx], item)


DEPTH = 10
WIDTH = 100
KEY   = Struct('140p')
INDEX = Struct('H')
COUNT = Struct('L')

COUNT_RES = Struct(KEY.format + COUNT.format)
SYNC_REQ  = Struct(INDEX.format + COUNT.format * WIDTH)


class RMBServer(DatagramServer):
    def start(self):
        super().start()
        self.cms = CountMinSketch(
            width=WIDTH,
            depth=DEPTH,
            )

    def handle(self, data, address):
        type = data[0]
        rest = memoryview(data)[1:]

        # add request
        if type == 0:
            key, = KEY.unpack(rest)
            self.cms.add(key)

        # count request
        elif type == 1:
            key, = KEY.unpack(rest)
            self.socket.sendto(
                COUNT_RES.pack(key, self.cms.count(key)),
                address,
                )

        # sync request
        elif type == 2:
            index, *counters = SYNC_REQ.unpack(data)
            merge(self.cms, index, counters)


if __name__ == '__main__':
    import sys
    RMBServer(sys.argv[1]).serve_forever()
