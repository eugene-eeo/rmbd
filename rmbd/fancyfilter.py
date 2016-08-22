from fnvhash import fnv1a_32


def khash(k, datum):
    for i in range(k):
        yield fnv1a_32(datum, i)


class FancyFilter:
    def __init__(self, width=400, depth=5):
        self.width = width
        self.depth = depth
        self.array = [[False]*self.width for _ in range(self.depth)]

    def add(self, datum):
        for row, h in zip(self.array, khash(self.depth, datum)):
            row[h % self.width] = True

    def has(self, datum):
        for row, h in zip(self.array, khash(self.depth, datum)):
            if not row[h % self.width]:
                return False
        return True


def merge(ff, index, counters):
    row = ff.array[index]
    for idx, item in enumerate(counters):
        row[idx] |= item
