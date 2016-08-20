from rmbd.protocol import KEY, PEER_REQ, SYNC_REQ, Type, parse, bit


addr = ('localhost', 9000)


def test_parse_add():
    req = parse(b'\x00' + KEY.pack(b'abc'))
    assert req == (Type.add, (b'abc',))


def test_parse_count():
    req = parse(b'\x01' + KEY.pack(b'abc'))
    assert req == (Type.count, (b'abc',))


def test_parse_sync():
    row = (0,) * 100
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
    for bit in range(5):
        tip = chr(bit).encode()
        data = b'random invalid data'
        # we don't care about body of ack requests
        if bit == 4:
            assert parse(tip) == (Type.ack, None)
            continue
        assert not parse(tip + data)


def test_bit():
    for item in Type:
        assert bit(item) == chr(item.value).encode()
