import gevent
from gevent.server import DatagramServer
from gevent.pool import Pool
from .service import Service


class Server(DatagramServer):
    def start(self, *args, **kwargs):
        super().start(*args, **kwargs)
        self.__service = Service(self.address, self.socket)

    def handle(self, data, addr):
        self.__service.dispatch(data, addr)

    def stop(self, *args, **kwargs):
        super().stop(*args, **kwargs)
        self.__service.stop()


def start_server(addr, max_connections=None):
    spawn = Pool(max_connections) if max_connections else gevent.spawn
    u = Server(addr, spawn=spawn)
    try:
        u.serve_forever()
    except KeyboardInterrupt:
        return
