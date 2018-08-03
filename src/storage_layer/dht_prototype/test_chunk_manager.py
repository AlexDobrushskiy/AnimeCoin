from masternode_modules.chunk_manager import ChunkManager
from masternode_modules.masternode import MasterNodeManager
from masternode_modules.settings import MasterNodeSettings

BASEDIR = "/home/synapse/tmp/animecoin/tmpstorage"
CHUNK_LIST = [
    "f03214550836c2a5c576a42e7522e3c844fa949dfd03456aa28d22fcc5832746",
    "9d79bb2f78a6e9f06cfb74715d30fde0ee863396be87c45a53eee9942f726d02",
    "d285f30e18eeeaaa2ca51b632478c9ce8a564e3e414142982ddda846dcb671be",
    "fd55893d6e255877f811d83009925c2bf8f34b6e207099a4bbd5ea09e358bb37",
    "b97b4fa39bd3ae847b32840131b9a604b259582531beae3bf38c686df48db797",
]

MASTERNODES = [
    ("e0ede7e4685350241b090982b81421f63a86de2c8a7ad15711414984dda4c433", "127.0.0.1", "86752", None),
    ("3cde740fe1b77084c7440db1d9863105646b792ebc0ca8d5b21e21c46f6216e1", "127.0.0.1", "86753", None),
    ("ede8bcce0703a1e31bf503ea5e43226295b410ef45ef4706b4c5ffba62210767", "127.0.0.1", "86754", None),
]


if __name__ == "__main__":
    masternode_settings = MasterNodeSettings(basedir=BASEDIR, replication_factor=15, )
    mn_manager = MasterNodeManager(MASTERNODES)
    x = ChunkManager(MASTERNODES[0][0], masternode_settings, CHUNK_LIST, mn_manager)
    # x.update_mn_list(MASTERNODES)
