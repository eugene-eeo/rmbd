from rmbd.protocol import KEY, PEER_REQ, SYNC_REQ, parse_request, Type


m = memoryview
b = lambda x: chr(x).encode()


def test_parse_add():
    req = parse_request(m(
        b(0) +
        KEY.pack(b'abc')
        ))
    assert req == (Type.add, (b'abc',))


def test_parse_count():
    req = parse_request(m(
        b(1) +
        KEY.pack(b'abc')
        ))
    assert req == (Type.count, (b'abc',))


def test_parse_sync():
    row = (0,) * 100
    req = parse_request(m(b(2) + SYNC_REQ.pack(1, *row)))
    assert req == (Type.sync, (1,) + row)


def test_parse_peer():
    req = parse_request(m(
        b(3) + PEER_REQ.pack(b'hostname', 1000)
        ))
    assert req == (Type.peer, (b'hostname', 1000))


def test_parse_invalid():
    assert not parse_request(b(1) + b'abc')
    assert not parse_request(b(4))
    assert not parse_request(b'')
