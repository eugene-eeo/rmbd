from string import ascii_lowercase
from rmbd.fancyfilter import FancyFilter, merge


def test_add_count():
    cms = FancyFilter(width=100, depth=10)
    cms.add(b'123')
    assert cms.has(b'123')


def test_merge():
    cms = FancyFilter(width=100, depth=10)
    cms.add(b'123')
    for i in range(cms.depth):
        merge(cms, i, [True]*cms.width)
    assert cms.has(b'123')
    for s in ascii_lowercase:
        assert cms.has(s.encode())
