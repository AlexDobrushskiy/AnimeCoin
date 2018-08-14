import json
import zstd

from dht_prototype.masternode_modules.animecoin_modules.animecoin_art_model import ArtTicket
from dht_prototype.masternode_modules.animecoin_modules.animecoin_compression import compress


if __name__ == "__main__":
    ticket = ArtTicket()
    d = ticket.to_dict()

    data = json.dumps(d)
    print("Original size: %s" % len(data))

    samples = [data.encode("utf-8")]
    cdict = zstd.train_dictionary(256, samples)

    compressed = compress(data)
    print("compressed without dict: %s" % len(compressed))

    compressed = compress(data, compressiondict=zstd.train_dictionary(256, samples))
    print("compressed with dict: %s" % len(compressed))
