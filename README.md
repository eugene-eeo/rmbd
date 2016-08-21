# rmbd

Experimental server that can replicate a count-min-sketch with other
instances by using a gossip protocol, for Python 3+ because reasons.
It is also a way for me to learn the lower level libraries and tools
in Python, e.g. buffers and structs.

## wat

Servers respond to 5 types of requests. Requests are in the form
`byte + param` where the first byte determines the type of request.
Refer to [struct](https://docs.python.org/3/library/struct.html)
for the formats.

|  type  | byte   | format   | description                                       | response     |
|:------:|--------|----------|---------------------------------------------------|--------------|
| add    | `\x00` | `!140p`  | count a key (`140p`)                              |              |
| count  | `\x01` | `!140p`  | count approximate occurences of key               | `!140pL`     |
| sync   | `\x02` | `!H100L` | updates the row (`100L`) at the given index (`H`) | `\x04` (ack) |
| peer   | `\x03` | `!140pL` | add a peer (`140p`, `L`) to the peers list        |              |
| ack    | `\x04` |          | acknowledge the successful sync of a row          |              |

When servers receive a `sync` request, they update their count-min-sketch
using the following algorithm:

```
def merge(peer, index, row):
    cms = cms_table[peer]
    for i, datum in enumerate(row):
        cms[index][i] = max(
            cms[index][i],
            datum,
            )
```

After a successful update servers will respond to the sender with
an `ack`.

Each server has a background sync task that sends the count-min-sketch
instance, row by row to other nodes by sending them `sync` requests.
After that it sleeps for a predefined delay and then removes the peers
which have not responded with an `ack`.

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
    >>> d.add(b'abc')
    >>> c.count(b'abc') # HOLY CRAP
    2
    >>> d.count(b'abc') # MUCH WOW
    2

## todo

 - make cli
 - implement fully automatic sync mechanism
