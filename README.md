# rmbd

Experimental server that can replicate a count-min-sketch with other
instances by using a gossip protocol, for Python 3+ because reasons.

    $ rmbd <host>:<port> -x <width> -y <depth>

It is also a way for me to learn the lower level libraries and tools
in Python, e.g. buffers and structs.

## wat

Servers respond to 5 types of messages:

|  type  | format        | description                                              | response     |
|:------:|---------------|----------------------------------------------------------|--------------|
| add    | `'\x00'+140p` | add a key (`140p`) to the internal count-min-sketch      |              |
| count  | `'\x01'+140p` | count approximate occurences of key                      | `140pL`      |
| sync   | `'\x02'+H100L`| updates the row at the given index (`H`)                 | `\x04` (ack) |
| peer   | `'\x03'+140pH`| add a peer (hostname=`140p`, port=`H`) to the peers list |              |
| ack    | `'\x04'`      | acknowledge the successful sync of a row                 |              |

`peer` is one way- sending it to a server means that the server will
now send `sync` requests to said peer. Once the peer receives the
sync requests it will reply with an `ack` if it was accepted.

Upon each `ack` request, the server updates  a table that maps the
peer to the receiving time. Disconnect detection of a peer in the
peer list is done by checking whether the ack time is larger than
the send time of a `sync` request.

## usage

The toolchain is a big WIP. Currently to start server:

    $ pip install -r requirements.txt
    $ python -m rmbd localhost:8000 &
      python -m rmbd localhost:9000

    # in a separate tab/split
    $ python
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
 - integration tests
