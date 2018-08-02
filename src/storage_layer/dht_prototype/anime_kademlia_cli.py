import sys

from .kademlia_module.kademlia_core import Kademlia, MASTER_ADDR


if __name__ == "__main__":
    cmdname = sys.argv[1]
    args = sys.argv[2:]

    dht = Kademlia("CMD", 9999, bootstrap=MASTER_ADDR)

    if cmdname == "get" and len(args) == 1:
        v = dht.get(args[0])
        print("Key data:", v)
    elif cmdname == "set" and len(args) == 2:
        dht.set(args[0], args[1])
    elif cmdname == "retrievefile" and len(args) == 1:
        file = dht.get(args[0])
        print("File data: %s" % file)
    elif cmdname == "storefile" and len(args) == 2:
        filedata = open(args[1], "rb").read()
        dht.set(args[0], filedata)
    elif cmdname == "storemany" and len(args) == 1:
        r = int(args[0])
        for i in range(r):
            k = i
            v = "hello-%s" % i
            dht.set(k, v)
    elif cmdname == "getmany" and len(args) == 1:
        r = int(args[0])
        for i in range(r):
            k = i
            v = "hello-%s" % i
            v = dht.get(k)
            print("Got: %s -> %s" % (k, v))
    else:
        print("Help:")
        print("Setting a key: set key value")
        print("Getting a key: get key")
        print("Getting help:  help")
