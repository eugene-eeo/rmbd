from collections import namedtuple
from struct import Struct
from enum import Enum


DEPTH = 10
WIDTH = 100
KEY   = Struct('140p')
INDEX = Struct('H')
COUNT = Struct('L')

COUNT_RES = Struct(KEY.format + COUNT.format)
SYNC_REQ  = Struct(INDEX.format + COUNT.format * WIDTH)


class Type(Enum):
    invalid = -1
    add = 0
    count = 1
    sync = 2


Request = namedtuple('Request', 'type,params')
InvalidRequest = Request(Type.invalid, ())


def parse_request(memview):
    type = memview[0]
    rest = memview[1:]

    if type == 0: return Request(Type.add,   KEY.unpack(rest))
    if type == 1: return Request(Type.count, KEY.unpack(rest))
    if type == 2: return Request(Type.sync,  SYNC_REQ.unpack(rest))
    return InvalidRequest
