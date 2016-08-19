from rmbd.countminsketch import CountMinSketch
from rmbd.service import handle_add, handle_count, handle_sync
from rmbd.protocol import COUNT_RES


def test_handle_add():
    res = []
    cms = CountMinSketch()
    handle_add(cms, res.append, (b'abc',))

    assert res == []
    assert cms.count(b'abc') == 1


def test_handle_count():
    r1 = []
    cms = CountMinSketch()
    handle_count(cms, r1.append, (b'abc',))
    assert r1 == [COUNT_RES.pack(b'abc', 0)]

    cms.add(b'abc')
    cms.add(b'abc')
    cms.add(b'def')

    r2 = []
    handle_count(cms, r2.append, (b'abc',))
    assert r2 == [COUNT_RES.pack(b'abc', 2)]

    r3 = []
    handle_count(cms, r3.append, (b'def',))
    assert r3 == [COUNT_RES.pack(b'def', 1)]


def test_handle_sync():
    res = []
    cms = CountMinSketch()
    handle_sync(cms, res.append, (0,) + (10,)*100)

    assert cms.array[0] == [10]*100
    assert res == []

    array = cms.array.copy()
    handle_sync(cms, res.append, (10,) + (10,)*100)

    assert cms.array == array
    assert res == []
