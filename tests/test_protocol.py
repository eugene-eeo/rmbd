from rmbd.protocol import ADD_REQ, HAS_REQ, PEER_REQ, SYNC_REQ, Type, parse, bit


def test_parse_add():
    req = parse(b'\x00' + ADD_REQ.pack(b'abc'))
    assert req == (Type.add, (b'abc',))


def test_parse_has():
    req = parse(b'\x01' + HAS_REQ.pack(b'abc'))
    assert req == (Type.has, (b'abc',))


def test_parse_sync():
    row = (True,) * 400
    req = parse(b'\x02' + SYNC_REQ.pack(1, *row))
    assert req == (Type.sync, (1,) + row)


def test_parse_peer():
    req = parse(b'\x03' + PEER_REQ.pack(b'hostname', 1000))
    assert req == (Type.peer, (b'hostname', 1000))


def test_parse_ack():
    req = parse(b'\x04')
    assert req == (Type.ack, None)


def test_parse_tip_invalid():
    assert not parse(b'\x05')
    assert not parse(b'')


def test_parse_payload_invalid():
    for bit in range(4):
        tip = chr(bit).encode()
        data = b'random invalid data'
        assert not parse(tip + data)
    assert parse(chr(4).encode() + b'random') == (Type.ack, None)


def test_bit():
    for item in Type:
        assert bit(item) == chr(item.value).encode()
