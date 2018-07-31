import random
import hashlib

from datetime import datetime as dt, timedelta as td

HASHLISTSIZE = 1000000

print("[+] Building hashlist")
hashlist = []
for i in range(HASHLISTSIZE):
    hashlist.append(random.getrandbits(1024*8).to_bytes(1024, byteorder="big"))

algos = sorted(hashlib.algorithms_guaranteed)
print("[+] Testing hash algorithms: %s" % algos)
for algo in algos:
    # shake has variable length digests, ignore it
    if algo.startswith('shake_'):
        continue

    algo_class = getattr(hashlib, algo)
    start = dt.now()
    for key in hashlist:
        m = algo_class()
        m.update(key)
        digest = m.digest()
    end = dt.now()

    total_time = (end-start).total_seconds()
    print("  [+] Algo %s in %.2f -> %.2f kh/s" % (algo, total_time, HASHLISTSIZE/total_time/1000))
print("[+] Done")
