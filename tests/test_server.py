import gevent
from gevent.server import DatagramServer
from rmbd.protocol import HAS_RES
from .utils import with_server, allocate_server, peer_request, add_request, has_request, retry


@with_server
def test_server_count_add(send, recv, _):
    send(add_request(b'abc'))
    send(add_request(b'abc'))
    send(has_request(b'abc'))

    key, exists = recv(HAS_RES)
    assert key == b'abc'
    assert exists


@with_server
def test_server_count_not_added(send, recv, _):
    send(has_request(b'key'))

    key, exists = recv(HAS_RES)
    assert key == b'key'
    assert not exists


@with_server
def test_one_way_sync(send, recv, _):
    with allocate_server() as peer:
        send(peer_request(peer.address))
        send(add_request(b'key'))

        @retry(3)
        def test():
            send(has_request(b'key'), peer.address)
            assert recv(HAS_RES) == (b'key', True)


@with_server
def test_two_way_sync(send, recv, a):
    with allocate_server() as b:
        send(peer_request(b.address), a.address)
        send(peer_request(a.address), b.address)

        send(add_request(b'key'), b.address)
        send(add_request(b'abc'), a.address)

        @retry(3)
        def test():
            send(has_request(b'abc'), b.address)
            assert recv(HAS_RES) == (b'abc', True)

        @retry(3)
        def test():
            send(has_request(b'key'), a.address)
            assert recv(HAS_RES) == (b'key', True)


@with_server
def test_path_guarantee(send, recv, a):
    with allocate_server() as b, allocate_server() as c, allocate_server() as d:
        send(peer_request(b.address), a.address)
        send(peer_request(c.address), b.address)
        send(peer_request(d.address), c.address)
        send(peer_request(a.address), d.address)

        send(add_request(b'key'), a.address)
        send(add_request(b'abc'), d.address)

        @retry(5)
        def test():
            send(has_request(b'key'), d.address)
            assert recv(HAS_RES) == (b'key', True)

        @retry(5)
        def test():
            send(has_request(b'abc'), c.address)
            assert recv(HAS_RES) == (b'abc', True)


@with_server
def test_inactive_client(send, recv, a):
    req = []
    def handler(data, addr):
        req.append(data)
    server = DatagramServer('localhost:0', handler)
    server.start()
    send(peer_request(server.address))

    @retry(3, delay=1, at_least=2)
    def test():
        assert len(req) == 5

    server.stop()


@with_server
def test_bad_data(send, recv, a):
    send(b'random binary gunk')
    send(add_request(b'key'))

    send(has_request(b'key'))
    # check that the server hasn't crashed
    assert recv(HAS_RES) == (b'key', True)
