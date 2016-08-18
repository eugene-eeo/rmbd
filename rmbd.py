import struct
import fnvhash
from gevent.server import DatagramServer


def khash(k, datum):
    for i in range(k):
        yield fnvhash.fnv1a_32(datum, i)


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


class RMBServer(DatagramServer):
    def start(self):
        super().start()
        self.__count_min_sketch = CountMinSketch(
            width=100,
            depth=10,
            )

    def handle(self, data, address):
        req_type = data[0]
        param    = memoryview(data, 1)

        # add request
        if req_type == ord('0'):
            self.__count_min_sketch.add(param)

        # count request
        elif req_type == ord('1'):
            count = self.__count_min_sketch.count(param)
            self.socket.sendto(
                struct.pack('L140p', count, param),
                address,
                )

        # sync request
        elif req_type == ord('2'):
            index, *counters = struct.unpack(
                'H' + 'L'*self.__count_min_sketch.width,
                param,
                )
            row = self.__count_min_sketch.array[index]
            row = [max(row[i], counters[i]) for i in range(len(row))]
            self.__count_min_sketch.array[index] = row


if __name__ == '__main__':
    RMBServer('localhost:9000').serve_forever()
