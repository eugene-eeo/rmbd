from fnvhash import fnv1a_32


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
