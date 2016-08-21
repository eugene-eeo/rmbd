from contextlib import contextmanager
from functools import wraps
import gevent
import gevent.socket as socket
from rmbd.server import Server
from rmbd.protocol import Type, bit, HAS_REQ, ADD_REQ, PEER_REQ


def add_request(key):
    return bit(Type.add) + ADD_REQ.pack(key)


def has_request(key):
    return bit(Type.has) + HAS_REQ.pack(key)


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
        raise error # pragma: no cover
    return run


def udp_socket():
    return socket.socket(type=socket.SOCK_DGRAM)


@contextmanager
def allocate_server():
    server = Server(('localhost', 0))
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
