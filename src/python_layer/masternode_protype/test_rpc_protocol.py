from .masternode_modules.rpc import serialize, deserialize


RPCNAME = "SPOTCHECK"
DATA = {"chunkid": 987654321, "start": 1234, "end": 56789}

req_packet = serialize(RPCNAME, DATA)
print(req_packet)
deserialized = deserialize(req_packet)
print(deserialized)
