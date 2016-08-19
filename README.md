# rmbd

Experimental server that can replicate a count-min-sketch with other
instances by using a gossip protocol.

    $ rmbd <host>:<port> -x <width> -y <depth>

It is also a way for me to learn the lower level libraries and tools
in Python, e.g. buffers and structs.

## wat

servers respond to 5 types of messages:

|  type  | format          | description                                              |
|:------:|-----------------|----------------------------------------------------------|
| add    | `'\x00' + 140p` | add a key (140p) to the internal count-min-sketch        |
| count  | `'\x01' + 140p` | count approximate occurences of key                      |
| sync   | `'\x02' + H100L`| update the row at the given index (`H`)                  |
| peer   | `'\x03' + 140pH`| add a peer (hostname=`140p`, port=`H`) to the peers list |
| ack    | `'\x04'`        | acknowledge the successful sync of a row                 |

## todo

 - rewrite with better code
 - implement fully automatic sync mechanism
 - add tests
