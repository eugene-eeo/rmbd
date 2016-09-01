from string import ascii_lowercase
from rmbd.bloomfilter import BloomFilter, merge, partition


def test_add_count():
    bf = BloomFilter()
    bf.add(b'123')
    assert bf.has(b'123')


def test_merge():
    bf = BloomFilter()
    bf.add(b'123')
    for i, _ in partition(bf):
        merge(bf, i, [True]*bf.width)
    assert bf.has(b'123')
    for s in ascii_lowercase:
        assert bf.has(s.encode())


def test_partition():
    bf = BloomFilter(width=2, depth=4)
    bf.array = [
        True, False,
        False, True,
        False, False,
        True, True,
        ]
    assert list(partition(bf)) == [
        (0, [True, False]),
        (1, [False, True]),
        (2, [False, False]),
        (3, [True, True]),
    ]
