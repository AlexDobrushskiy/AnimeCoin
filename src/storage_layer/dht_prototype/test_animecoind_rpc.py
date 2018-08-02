from bitcoinrpc.authproxy import AuthServiceProxy


IP, PORT = "127.0.0.1", "19932"
RPCUSER = "test"
RPCPASSWORD = "testpw"
ADDRESS = "http://%s:%s@%s:%s" % (RPCUSER, RPCPASSWORD, IP, PORT)

if __name__ == "__main__":
    rpc_connection = AuthServiceProxy(ADDRESS)
    best_block_hash = rpc_connection.getbestblockhash()
    print(rpc_connection.getblock(best_block_hash))
