from rmbd.protocol import KEY, SYNC_REQ, parse_request, Request, Type


m = memoryview
b = lambda x: chr(x).encode()


def test_parse_add():
    req = parse_request(m(
        b(0) +
        KEY.pack(b'abc')
        ))
    assert req == Request(Type.add, (b'abc',))


def test_parse_count():
    req = parse_request(m(
        b(1) +
        KEY.pack(b'abc')
        ))
    assert req == Request(Type.count, (b'abc',))


def test_parse_sync():
    row = (0,) * 100
    req = parse_request(m(b(2) + SYNC_REQ.pack(1, *row)))
    assert req == Request(Type.sync, (1,) + row)


def test_parse_invalid():
    assert not parse_request(b(3))
    assert not parse_request(b(1) + b'abc')
