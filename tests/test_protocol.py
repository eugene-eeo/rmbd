from rmbd.protocol import KEY, PEER_REQ, SYNC_REQ, Type, parse, bit, Request


addr = ('localhost', 9000)


def test_parse_add():
    req = parse(bit(Type.add) + KEY.pack(b'abc'), addr)
    assert req == Request(Type.add, (b'abc',), addr)


def test_parse_count():
    req = parse(bit(Type.count) + KEY.pack(b'abc'), addr)
    assert req == Request(Type.count, (b'abc',), addr)


def test_parse_sync():
    row = (0,) * 100
    req = parse(bit(Type.sync) + SYNC_REQ.pack(1, *row), addr)
    assert req == Request(Type.sync, (1,) + row, addr)


def test_parse_peer():
    req = parse(bit(Type.peer) + PEER_REQ.pack(b'hostname', 1000), addr)
    assert req == Request(Type.peer, (b'hostname', 1000), addr)


def test_parse_ack():
    req = parse(bit(Type.ack), addr)
    assert req == Request(Type.ack, None, addr)


def test_parse_invalid():
    assert not parse(b'\x00' + b'abc', addr)
    assert not parse(b'\x05', addr)
    assert not parse(b'', addr)


def test_bit():
    for item in Type:
        b_ = bit(item)
        assert isinstance(b_, bytes)
        assert b_[0] == item.value
        assert b_ == chr(item.value).encode()
