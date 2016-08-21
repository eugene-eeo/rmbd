from contextlib import contextmanager
from functools import wraps
import gevent
import gevent.socket as socket
from rmbd.server import Server
from rmbd.protocol import Type, bit, COUNT_REQ, ADD_REQ, COUNT_RES, PEER_REQ


def add_request(key):
    return bit(Type.add) + ADD_REQ.pack(key)


def count_request(key):
    return bit(Type.count) + COUNT_REQ.pack(key)


def peer_request(peer):
    host, port = peer
    return bit(Type.peer) + PEER_REQ.pack(host.encode(), port)


def retry(times, delay=0.5):
    def run(fn, n=times):
        error = None
        while n > 0:
            try:
                fn()
                return
            except Exception as err:
                error = err
                pass
            n -= 1
            gevent.sleep(delay)
        raise error
    return run


def udp_socket():
    return socket.socket(type=socket.SOCK_DGRAM)


@contextmanager
def allocate_server(ADDR=[8000]):
    ADDR[0] += 1
    server = Server(('localhost', ADDR[0]))
    server.start()
    try:
        yield server
    finally:
        server.stop()


def with_server(wrapped):
    @wraps(wrapped)
    def fn():
        sock = udp_socket()
        with allocate_server() as server:
            wrapped(
                lambda b, p=server.address: sock.sendto(b, p),
                lambda f: f.unpack(sock.recv(f.size)),
                server,
            )
            server.stop()
    return fn


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
