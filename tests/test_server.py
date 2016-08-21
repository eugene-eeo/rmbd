from gevent.server import DatagramServer
from rmbd.protocol import COUNT_RES
from .utils import *


@with_server
def test_server_count_add(send, recv, _):
    send(add_request(b'abc'))
    send(add_request(b'abc'))
    send(count_request(b'abc'))

    key, count = recv(COUNT_RES)
    assert key == b'abc'
    assert count == 2


@with_server
def test_server_count_not_added(send, recv, _):
    send(count_request(b'key'))

    key, count = recv(COUNT_RES)
    assert key == b'key'
    assert count == 0


@with_server
def test_one_way_sync(send, recv, _):
    with allocate_server() as peer:
        send(peer_request(peer.address))
        send(add_request(b'key'))

        @retry(3)
        def test():
            send(count_request(b'key'), peer.address)
            assert recv(COUNT_RES) == (b'key', 1)


@with_server
def test_two_way_sync(send, recv, a):
    with allocate_server() as b:
        send(peer_request(b.address), a.address)
        send(peer_request(a.address), b.address)

        send(add_request(b'key'), b.address)
        send(add_request(b'key'), a.address)

        @retry(3)
        def test():
            send(count_request(b'key'), b.address)
            assert recv(COUNT_RES) == (b'key', 2)

        send(count_request(b'key'), a.address)
        assert recv(COUNT_RES) == (b'key', 2)


@with_server
def test_inactive_client_is_disconnected(send, recv, server):
    requests = []

    class InactiveClient(DatagramServer):
        def handle(self, data, peer):
            requests.append(data)

    inactive = InactiveClient(('localhost', 0))
    send(peer_request(inactive.address), server.address)

    @retry(3)
    def test_no_more_requests():
        current_size = len(requests)
        gevent.sleep()
        assert len(requests) == current_size
