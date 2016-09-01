from fnvhash import fnv1a_32


def khash(k, datum):
    for i in range(k):
        yield fnv1a_32(datum, i)


class FancyFilter:
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


def merge(ff, offset, counters):
    for idx, item in enumerate(counters):
        ff.array[offset*ff.width + idx] |= item


def partition(ff):
    width = ff.width
    for i in range(ff.depth):
        start = i * width
        yield i, ff.array[start:start+width]
