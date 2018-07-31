import random
import hashlib

from datetime import datetime as dt, timedelta as td


NODE_SEED = b'/Q\xe0\xbftE+\xff4YpA\t\x96\xa1`\xc6)\xe2\xad\x0c\xf4\xa9\xf0\xa9_Ir\xc0\x8aw\xb0'
KEY_SEED = b"\r\xfd\x9a\x84'\x06>\xf8\x0e\xb4[\xcc\x94\xb8\x08m\xfa\xd9\x0fV`\\s*\x87H>d\x95Y^$"
ALIAS_SEED = b'd\xad`n\xdc\x89\xc2/\xf6\xcd\xd6\xec\xcc\x1c\xc7\xd4\x83B9\x01\xb4\x06\xa2\xc9=\xf8_\x98\xa1p\x01&'

NODE_NUM = 100
KEY_NUM = 1000 * 1000
KEY_REPLICATION_FACTOR = 10


def getrandbytes(n):
    return random.getrandbits(n * 8).to_bytes(n, byteorder="big")


def get_digest(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.digest()


def generate_alternate_keys(replication_db, original_id):
    # print("[+] Original key: %s (%s)" % (original_id, original_key))

    alternate_keys = []
    for repl_num, repl_digest in replication_db.items():
        alt_key = repl_digest ^ original_id
        # print(" [+] Generated replication key %s -> %s" % (repl_num, alt_key))
        alternate_keys.append(alt_key)
    return alternate_keys


def findclosest(nodes, key):
    best, min_distance = None, None
    for nodename, nodeid in nodes.items():
        distance = nodeid ^ key
        if best is None or distance < min_distance:
            best = nodename
            min_distance = distance
    return best


def generate_node_databases(node_number, keys, nodes, replication_db):
    file_database = {}
    key_alias_database = {}

    my_nodeid = nodes[node_number]

    other_nodes = []
    for nodenumber, nodeid in nodes.items():
        if nodenumber != node_number:
            other_nodes.append(nodeid)

    for original_id in keys:
        for repl_num, repl_digest in replication_db.items():
            alt_key = repl_digest ^ original_id

            my_distance = alt_key ^ my_nodeid

            store = True
            for othernodeid in other_nodes:
                if alt_key ^ othernodeid < my_distance:
                    store = False
                    break

            if store:
                file_database[original_id] = True
                key_alias_database[alt_key] = original_id

    return file_database, key_alias_database


def main():
    print("[+] Generating replication DB")
    replication_db = {}
    for i in range(KEY_REPLICATION_FACTOR):
        digest = get_digest(i.to_bytes(4, byteorder='big') + ALIAS_SEED)
        replication_db[i] = int.from_bytes(digest, byteorder='big')

    print("[+] Generating node ids")
    nodes = {}
    for node in range(NODE_NUM):
        node_key = NODE_SEED + node.to_bytes(8, byteorder='big')
        nodeid = int.from_bytes(get_digest(node_key), byteorder='big')
        nodes[node] = nodeid
        print("Generated node: %s, nodeid: %s" % (node, nodeid))

    print("[+] Generating %s keys" % KEY_NUM)
    keys = []
    for i in range(KEY_NUM):
        data = getrandbytes(128)
        data_digest = get_digest(data)
        data_key = int.from_bytes(data_digest, byteorder='big')
        keys.append(data_key)

    # print("[+] Assigning keys to NODES")
    # for original_id in keys:
    #     replication_nodes = []
    #     alternate_keys = generate_alternate_keys(replication_db, original_id)
    #     for alt_key in alternate_keys:
    #         closest_node = findclosest(nodes, alt_key)
    #         replication_nodes.append(closest_node)
    #     print(" [+] Replication list: %s" % replication_nodes)
    #
    #     for i in range(NODE_NUM):
    #         c = replication_nodes.count(i)
    #         print("Node %s: %s" % (i, c))

    print("[+] Figure out which keys belong to Node 0")
    start = dt.now()
    file_database, key_alias_database = generate_node_databases(0, keys, nodes, replication_db)
    end = dt.now()
    elapsed = (end - start).total_seconds()
    print("DONE in %s" % elapsed)

    print("#" * 100)
    print("[+] Done, analysing allocation strategy")

    total_keys = KEY_NUM
    total_aliases = KEY_NUM * KEY_REPLICATION_FACTOR
    print("[+] Node alias database: %s -> %.2f%%" % (
        len(key_alias_database),
        len(key_alias_database) / total_aliases * 100,
    ))
    print("[+] File database: %s -> %.2f%%" % (
        len(file_database),
        len(file_database) / total_keys * 100,
    ))


if __name__ == "__main__":
    main()
