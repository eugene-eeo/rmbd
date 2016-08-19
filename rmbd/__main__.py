import sys
from rmbd.service import RMBServer


if __name__ == '__main__':
    RMBServer(sys.argv[1]).serve_forever()
