import logging
import asyncio
from kademlia.network import Server

# # setting up logging
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# # TODO: hack, we have to emit a log message for this to work in the kamelia module, no idea why
# logging.info("HI")


class Kademlia:
    def __init__(self, nodename, port, bootstrap=None):
        self.__nodename = nodename

        self.__node = Server()
        self.__node.listen(port)
        self.__loop = asyncio.get_event_loop()

        if bootstrap is not None:
            # Bootstrap the node by connecting to other known nodes, in this case
            # replace 123.123.123.123 with the IP of another node and optionally
            # give as many ip/port combos as you can for other nodes.
            self.__loop.run_until_complete(self.__node.bootstrap([(bootstrap[0], bootstrap[1])]))

    def set(self, k, v):
        self.__loop.run_until_complete(self.__node.set(k, v))

    def get(self, k):
        v = self.__loop.run_until_complete(self.__node.get(k))
        return v

    def run_forever(self):
        self.__loop.run_forever()
