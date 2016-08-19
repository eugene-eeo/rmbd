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

Request = namedtuple('Request', 'type,params')


class Type(Enum):
    add = 0
    count = 1
    sync = 2


def parse_request(memview):
    type = Type(memview[0])
    rest = memview[1:]

    if type == Type.add or type == Type.count:
        return Request(type, KEY.unpack(rest))

    elif type == Type.sync:
        index, *counters = SYNC_REQ.unpack(rest)
        return Request(type, (index, counters))
