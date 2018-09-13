from django.db import models
from django.conf import settings
from dht_prototype.masternode_modules.masternode_communication import NodeManager
from dht_prototype.masternode_modules.masternode_discovery import discover_nodes

# discover animecoin nodes
nodemanager = NodeManager()
for settings in discover_nodes(settings.ANIMECOIN_BINARY_PATH, settings.ANIMECOIN_NODES_PATH):
    nodemanager.add_masternode(settings["nodeid"], settings["ip"], settings["port"], settings["pubkey"])
