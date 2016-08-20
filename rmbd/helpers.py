from time import time
import gevent.socket as socket


def normalize(addr):
    host, port = addr
    return (socket.gethostbyname(host), port)


def get_outdated(acks, last_sent):
    for peer in last_sent:
        if acks.get(peer, 0) < last_sent[peer]:
            yield peer


def broadcast(socket, peers, packet):
    for peer in peers:
        socket.sendto(packet, peer)
        yield peer, time()
