from .countminsketch import CountMinSketch, merge
from .protocol import parse_request, COUNT_RES, Type, WIDTH, DEPTH
from gevent.server import DatagramServer


def handle_add(cms, send, params):
    key, = params
    cms.add(key)


def handle_count(cms, send, params):
    key, = params
    send(COUNT_RES.pack(key, cms.count(key)))


def handle_sync(cms, send, params):
    index, *row = params
    if index < cms.depth:
        merge(cms, index, row)


class RMBServer(DatagramServer):
    handlers = {
        Type.add:   handle_add,
        Type.count: handle_count,
        Type.sync:  handle_sync,
    }

    def start(self):
        super().start()
        self.cms = CountMinSketch(
            width=WIDTH,
            depth=DEPTH,
            )

    def handle(self, data, address):
        request = parse_request(memoryview(data))
        if not request:
            return
        self.handlers[request.type](
            self.cms,
            lambda data: self.socket.sendto(data, address),
            request.params,
            )
