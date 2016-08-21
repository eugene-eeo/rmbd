# rmbd

Experimental server that can replicate an adapted bloom filter with other
instances by using a gossip protocol, for Python 3+ because reasons.
It is also a way for me to learn the lower level libraries and tools
in Python, e.g. buffers and structs. It guarantees that if you have at
least one one-way path from node A to node B, changes in A will be
reflected in B.

## wat

Servers respond to 5 types of requests. Requests are in the form
`byte + param` where the first byte determines the type of request.
Refer to [struct](https://docs.python.org/3/library/struct.html)
for the formats.

| type | byte   | format   | description                                       | response     |
|:----:|--------|----------|---------------------------------------------------|--------------|
| add  | `\x00` | `!140p`  | add a key (`140p`)                                |              |
| has  | `\x01` | `!140p`  | query the existence of a key (`140p`)             | `!140p?`     |
| sync | `\x02` | `!H400?` | updates the row (`400?`) at the given index (`H`) | `\x04` (ack) |
| peer | `\x03` | `!140pL` | add a peer (`140p`, `L`) to the peers list        |              |
| ack  | `\x04` |          | acknowledge the successful sync of a row          |              |

When servers receive a `sync` request, they update their filters
using the following algorithm:

    def merge(index, row):
        for i, bit in enumerate(row):
            filter[index][i] |= bit

After a successful update servers will respond to the sender with
an `ack`.

Each server has a background sync task that sends the filter, row by
row to other nodes by sending them `sync` requests. After that it
sleeps for a predefined delay and then removes the peers which have
not responded with an `ack`.

## usage

The toolchain is a big WIP. Currently to start server:

    $ pip install -r requirements.txt
    $ python -m rmbd localhost:8000 & python -m rmbd localhost:9000

And then to make them talk to each other:

    >>> from client import RmbdClient
    >>> c = RmbdClient((b'localhost', 8000))
    >>> d = RmbdClient((b'localhost', 9000))

    # two way sync
    >>> c.peer((b'localhost', 9000))
    >>> d.peer((b'localhost', 8000))

    >>> c.add(b'abc')
    >>> d.add(b'def')
    >>> c.has(b'def') # HOLY CRAP
    True
    >>> d.has(b'abc') # MUCH WOW
    True

## dev

    $ pip install coverage nose
    $ nosetests --with-coverage --cover-package=rmbd

## todo

 - make cli
 - implement fully automatic sync mechanism
