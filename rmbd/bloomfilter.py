from fnvhash import fnv1a_32


def khash(k, datum):
    for i in range(k):
        yield fnv1a_32(datum, i)


class BloomFilter:
    def __init__(self, width=400, depth=5):
        self.width = width
        self.depth = depth
        self.dim = width * depth
        self.array = [False for _ in range(self.dim)]

    def add(self, datum):
        for h in khash(self.depth, datum):
            self.array[h % self.dim] = True

    def has(self, datum):
        for h in khash(self.depth, datum):
            if not self.array[h % self.dim]:
                return False
        return True


def merge(bf, offset, counters):
    for idx, item in enumerate(counters):
        bf.array[offset*bf.width + idx] |= item


def partition(bf):
    width = bf.width
    for i in range(bf.depth):
        start = i * width
        yield i, bf.array[start:start+width]
