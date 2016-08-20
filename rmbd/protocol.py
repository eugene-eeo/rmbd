from collections import namedtuple
from struct import Struct, error
from enum import Enum


DEPTH = 10
WIDTH = 100
KEY   = Struct('!140p')
COUNT_RES = Struct('!140pL')
PEER_REQ  = Struct('!140pL')
SYNC_REQ  = Struct('!H100L')

Request = namedtuple('Request', 'type,params,peer')


class Type(Enum):
    add   = 0
    count = 1
    sync  = 2
    peer  = 3
    ack   = 4


def bit(type):
    return chr(type.value).encode()


def try_unpack(type, struct, data):
    try:
        return type, struct.unpack(data)
    except error:
        return None


def parse_request(memview):
    if not len(memview):
        return None

    type = memview[0]
    rest = memview[1:]

    if type == 0: return try_unpack(Type.add,   KEY, rest)
    if type == 1: return try_unpack(Type.count, KEY, rest)
    if type == 2: return try_unpack(Type.sync,  SYNC_REQ, rest)
    if type == 3: return try_unpack(Type.peer,  PEER_REQ, rest)
    if type == 4: return (Type.ack, None)
    return None


def parse(data, peer):
    req = parse_request(memoryview(data))
    if req:
        type, params = req
        return Request(
                type=type,
                peer=peer,
                params=params,
            )
