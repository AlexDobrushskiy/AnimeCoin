import math
import os
import hashlib

from core_modules.helpers_type import ensure_type_of_field


class MNDeamonSettings:
    def __init__(self, settings):
        self.cdaemon_conf = ensure_type_of_field(settings, "cdaemon_conf", str)
        self.showmetrics = ensure_type_of_field(settings, "showmetrics", str)
        self.rpcuser = ensure_type_of_field(settings, "rpcuser", str)
        self.rpcpassword = ensure_type_of_field(settings, "rpcpassword", str)
        self.port = ensure_type_of_field(settings, "port", int)
        self.rpcport = ensure_type_of_field(settings, "rpcport", int)
        self.listenonion = ensure_type_of_field(settings, "listenonion", str)
        self.nodename = ensure_type_of_field(settings, "nodename", str)
        self.nodeid = ensure_type_of_field(settings, "nodeid", int)
        self.datadir = ensure_type_of_field(settings, "datadir", str)
        self.basedir = ensure_type_of_field(settings, "basedir", str)
        self.ip = ensure_type_of_field(settings, "ip", str)
        self.pyrpcport = ensure_type_of_field(settings, "pyrpcport", int)
        self.pyhttpadmin= ensure_type_of_field(settings, "pyhttpadmin", int)
        self.pubkey = ensure_type_of_field(settings, "pubkey", str)


# CONFIG_FILE_NAME = "masternode.cfg"
# DEFAULT_SETTINGS = {
#     "blockchain": {
#         "rpcuser": "test",
#         "rpcpassword": "testpw",
#         "rpcport": "10340",
#         "port": "12340",
#     }
# }
#
# class MasterNodeConfigParser:
#     def __init__(self, basedir):
#         self.__basedir = basedir
#         self.__configname = os.path.join(self.__basedir, CONFIG_FILE_NAME)
#         self.settings = None
#
#         self.__load_config_file()
#
#     def __load_config_file(self):
#         try:
#             settings = json.load(open(self.__configname))
#         except FileNotFoundError:
#             print("Config file not found, generating a default one")
#             settings = {}
#
#         # set fields from default if they doesn't exist
#         merged_settings = DEFAULT_SETTINGS.copy()
#         for k, v in settings.items():
#             # ignore keys we no longer use
#             if k not in merged_settings:
#                 print("Config key %s is no longer supported!" % k)
#             merged_settings[k] = v
#         self.settings = merged_settings
#         self.save()
#
#     def save(self):
#         json.dump(self.settings, open(self.__configname, "w"), indent=4, sort_keys=True)


# NETWORK SETTINGS - global settings for everyone
class __NetworkSettings:
    pass


NetWorkSettings = __NetworkSettings()

NetWorkSettings.DEBUG = True

if NetWorkSettings.DEBUG:
    NetWorkSettings.VALIDATE_MN_SIGNATURES = False
else:
    NetWorkSettings.VALIDATE_MN_SIGNATURES = True

NetWorkSettings.BLOCKCHAIN = "animecoind"
if NetWorkSettings.BLOCKCHAIN == "bitcoind":
    NetWorkSettings.BLOCKCHAIN_BINARY = "/home/synapse/tmp/bitcoind_old/bitcoin/src/bitcoind"
    NetWorkSettings.BASE_TRANSACTION_AMOUNT = 0.000001
    NetWorkSettings.COIN = 100000000  # satoshis in 1 btc
    NetWorkSettings.CDAEMON_CONFIG_FILE = "animecoin.conf"
else:
    # animecoind
    NetWorkSettings.BLOCKCHAIN_BINARY = "/home/synapse/dev/toptal/animecoin/code/animecoin_blockchain/AnimeCoin/src/animecoind"
    NetWorkSettings.COIN = 100000
    NetWorkSettings.BASE_TRANSACTION_AMOUNT = 300.0/NetWorkSettings.COIN  #0.00300
    NetWorkSettings.CDAEMON_CONFIG_FILE = "animecoin.conf"


if NetWorkSettings.DEBUG:
    NetWorkSettings.REQUIRED_CONFIRMATIONS = 1
else:
    NetWorkSettings.REQUIRED_CONFIRMATIONS = 10

NetWorkSettings.PYTHONPATH = "python"
NetWorkSettings.BASEDIR = os.path.abspath(os.path.join(__file__, "..", ".."))
NetWorkSettings.DJANGO_ROOT = os.path.join(NetWorkSettings.BASEDIR, "client_prototype", "django_frontend")

NetWorkSettings.ALIAS_SEED = b'd\xad`n\xdc\x89\xc2/\xf6\xcd\xd6\xec\xcc\x1c\xc7\xd4\x83B9\x01\xb4\x06\xa2\xc9=\xf8_\x98\xa1p\x01&'
NetWorkSettings.CNODE_HASH_ALGO = hashlib.sha256
NetWorkSettings.PYNODE_HASH_ALGO = hashlib.sha3_512
NetWorkSettings.CNODE_HEX_DIGEST_SIZE = NetWorkSettings.CNODE_HASH_ALGO().digest_size * 2
NetWorkSettings.PYNODE_HEX_DIGEST_SIZE = NetWorkSettings.PYNODE_HASH_ALGO().digest_size * 2

# TODO: set this to something more reasonable, perhaps set it per RPC call with ACLs?
NetWorkSettings.RPC_MSG_SIZELIMIT = 100*1024*1024        # 100MB

NetWorkSettings.REPLICATION_FACTOR = 15
NetWorkSettings.CHUNKSIZE = 1 * 1024*1024                # 1MB

NetWorkSettings.MAX_TICKET_SIZE = 75 * 1024              # 75kbyte
NetWorkSettings.IMAGE_MAX_SIZE = 100 * 1024*1024         # 100MB
NetWorkSettings.MAX_REGISTRATION_BLOCK_DISTANCE = 3      # 3 blocks

NetWorkSettings.THUMBNAIL_DIMENSIONS = (240, 240)
NetWorkSettings.THUMBNAIL_MAX_SIZE = 100 * 1024          # 100 kb

NetWorkSettings.LUBY_REDUNDANCY_FACTOR = 10

NetWorkSettings.MAX_LUBY_CHUNKS = math.ceil((NetWorkSettings.IMAGE_MAX_SIZE / NetWorkSettings.CHUNKSIZE) \
                                  * NetWorkSettings.LUBY_REDUNDANCY_FACTOR)


NetWorkSettings.NSFW_MODEL_FILE = "/home/synapse/tmp/animecoin/nsfw/nsfw_trained_model.pb"
if NetWorkSettings.DEBUG:
    NetWorkSettings.NSFW_THRESHOLD = 0.999
else:
    NetWorkSettings.NSFW_THRESHOLD = 0.7

if NetWorkSettings.DEBUG:
    NetWorkSettings.DUPE_DETECTION_ENABLED = False
    NetWorkSettings.DUPE_DETECTION_MODELS = ["VGG16"]
    NetWorkSettings.DUPE_DETECTION_FINGERPRINT_SIZE = 512
    # NetWorkSettings.DUPE_DETECTION_MODELS = ["VGG16", "Xception", "InceptionResNetV2", "DenseNet201", "InceptionV3"]
    # NetWorkSettings.DUPE_DETECTION_FINGERPRINT_SIZE = 8064
else:
    NetWorkSettings.DUPE_DETECTION_ENABLED = True
    NetWorkSettings.DUPE_DETECTION_MODELS = ["VGG16", "Xception", "InceptionResNetV2", "DenseNet201", "InceptionV3"]
    NetWorkSettings.DUPE_DETECTION_FINGERPRINT_SIZE = 8064

NetWorkSettings.DUPE_DETECTION_TARGET_SIZE = (240, 240)   # the dupe detection modules were trained with this size
NetWorkSettings.DUPE_DETECTION_SPEARMAN_THRESHOLD = 0.86
NetWorkSettings.DUPE_DETECTION_KENDALL_THRESHOLD = 0.80
NetWorkSettings.DUPE_DETECTION_HOEFFDING_THRESHOLD = 0.48
NetWorkSettings.DUPE_DETECTION_STRICTNESS = 0.99
NetWorkSettings.DUPE_DETECTION_KENDALL_MAX = 0
NetWorkSettings.DUPE_DETECTION_HOEFFDING_MAX = 0

if NetWorkSettings.DEBUG:
    NetWorkSettings.BLOCKCHAIN_SEED_ADDR = "127.0.0.1:12340"
else:
    # TODO: fill this out for prod
    NetWorkSettings.BLOCKCHAIN_SEED_ADDR = ""
# END
