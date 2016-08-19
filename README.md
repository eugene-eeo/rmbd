# rmbd

Experimental server that can replicate a count-min-sketch with other
instances by using a gossip protocol.

    $ rmbd <host>:<port> -x <width> -y <depth>

It is also a way for me to learn the lower level libraries and tools
in Python, e.g. buffers and structs.

## wat

Servers respond to 5 types of messages:

|  type  | format        | description                                              | response     |
|:------:|---------------|----------------------------------------------------------|--------------|
| add    | `'\x00'+140p` | add a key (140p) to the internal count-min-sketch        |              |
| count  | `'\x01'+140p` | count approximate occurences of key                      | `140pL`      |
| sync   | `'\x02'+H100L`| updates the row at the given index (`H`)                 | `\x04` (ack) |
| peer   | `'\x03'+140pH`| add a peer (hostname=`140p`, port=`H`) to the peers list |              |
| ack    | `'\x04'`      | acknowledge the successful sync of a row                 |              |

Upon each `ack` request, the server sets the time of receiving into
a table that maps the peer to the receiving time. Disconnection of
a peer in the peer list is done by checking whether the ack time is
larger than the send time of a `sync` request.

`peer` is one way- sending it to a server means that the server will
now send `sync` requests to said peer.

## todo

 - make cli
 - implement fully automatic sync mechanism
 - integration tests
