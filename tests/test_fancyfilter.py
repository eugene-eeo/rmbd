from string import ascii_lowercase
from rmbd.fancyfilter import FancyFilter, merge, partition


def test_add_count():
    ff = FancyFilter(width=100, depth=10)
    ff.add(b'123')
    assert ff.has(b'123')


def test_merge():
    ff = FancyFilter(width=100, depth=10)
    ff.add(b'123')
    for i, _ in partition(ff):
        merge(ff, i, [True]*ff.width)
    assert ff.has(b'123')
    for s in ascii_lowercase:
        assert ff.has(s.encode())


def test_partition():
    ff = FancyFilter(width=2, depth=4)
    ff.array = [
        True, False,
        False, True,
        False, False,
        True, True,
        ]
    assert list(partition(ff)) == [
        (0, [True, False]),
        (1, [False, True]),
        (2, [False, False]),
        (3, [True, True]),
    ]
