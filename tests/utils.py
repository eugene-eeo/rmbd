from contextlib import contextmanager
from functools import wraps
import gevent
import gevent.socket as socket
from rmbd.server import Server
from rmbd.protocol import Type, bit, HAS_REQ, ADD_REQ, PEER_REQ, SYNC_REQ


def add_request(key):
    return bit(Type.add) + ADD_REQ.pack(key)


def has_request(key):
    return bit(Type.has) + HAS_REQ.pack(key)


def peer_request(peer):
    host, port = peer
    return bit(Type.peer) + PEER_REQ.pack(host.encode(), port)


def sync_request(offset, row):
    return bit(Type.sync) + SYNC_REQ.pack(offset, *row)


def retry(times, delay=0.5, at_least=1): # pragma: no cover
    def run(fn, n=times, t=at_least):
        error = None
        while n > 0:
            try:
                fn()
                t -= 1
                if not t: return
            except Exception as err:
                error = err
                pass
            n -= 1
            gevent.sleep(delay)
        if t != 0:
            raise error
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
            sock.close()
    return fn
