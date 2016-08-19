from collections import namedtuple
from struct import Struct, error
from enum import Enum


DEPTH = 10
WIDTH = 100
KEY   = Struct('140p')
INDEX = Struct('H')
COUNT = Struct('L')

COUNT_RES = Struct(KEY.format + COUNT.format)
PEER_REQ  = Struct(KEY.format + COUNT.format)
SYNC_REQ  = Struct(INDEX.format + COUNT.format * WIDTH)


class Type(Enum):
    add   = 0
    count = 1
    sync  = 2
    peer  = 3
    ack   = 4


Request = namedtuple('Request', 'type,params,peer')


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
