import struct
from collections import namedtuple
from enum import Enum


ADD_REQ = struct.Struct('!140p')
HAS_REQ = struct.Struct('!140p')
HAS_RES = struct.Struct('!140p?')
PEER_REQ = struct.Struct('!140pL')
SYNC_REQ = struct.Struct('!H400?')

Request = namedtuple('Request', 'type,params,peer')


class Type(Enum):
    add = 0
    has = 1
    sync = 2
    peer = 3
    ack = 4


def bit(type):
    return chr(type.value).encode()


def try_unpack(type, format, data):
    try:
        return type, format.unpack(data)
    except struct.error:
        return None


def parse(data):
    if not len(data):
        return None

    type = data[0]
    rest = memoryview(data)[1:]

    if type == 0: return try_unpack(Type.add,  ADD_REQ, rest)
    if type == 1: return try_unpack(Type.has,  HAS_REQ, rest)
    if type == 2: return try_unpack(Type.sync, SYNC_REQ, rest)
    if type == 3: return try_unpack(Type.peer, PEER_REQ, rest)
    if type == 4: return (Type.ack, None)
    return None
