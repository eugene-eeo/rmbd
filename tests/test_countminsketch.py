from string import ascii_lowercase
from rmbd.countminsketch import CountMinSketch, merge


def test_cms_add_count():
    cms = CountMinSketch(width=100, depth=10)
    cms.add(b'123')
    cms.add(b'123')
    assert cms.count(b'123') == 2
    assert cms.count(b'not exists') == 0


def test_merge():
    cms = CountMinSketch(width=100, depth=10)
    cms.add(b'123')
    for i in range(cms.depth):
        merge(cms, i, [10]*cms.width)
    assert cms.count(b'123') == 10
    for s in ascii_lowercase:
        assert cms.count(s.encode()) == 10
