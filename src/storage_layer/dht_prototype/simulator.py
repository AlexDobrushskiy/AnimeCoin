from flask import Flask

import time
import logging
from multiprocessing import Process

from dht_prototype.kademlia_module.kademlia_core import Kademlia, MASTER_ADDR

# setting up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# TODO: hack, we have to emit a log message for this to work in the kamelia module, no idea why
logging.info("HI")

BASEPORT = 12345


def run_kademlia_node(nodename, portnum, bootstrap=None):
    k = Kademlia(nodename, portnum, bootstrap=bootstrap)
    time.sleep(1)
    k.set(str(nodename), "%s hello" % nodename)
    k.run_forever()


def main():
    processes = []
    for i in range(0, 10):
        nodename, portnum = "node_%s" % i, BASEPORT+i

        if i == 0:
            bootstrap = None
        else:
            bootstrap = MASTER_ADDR

        print("Starting nodename: %s, port: %s, bootstrap: %s" % (nodename, portnum, bootstrap))
        p = Process(target=run_kademlia_node, args=(nodename, portnum, bootstrap))
        p.start()
        processes.append(p)

    print("Daemons spawned, Ctrl-C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for p in processes:
            print("Strpping process %s" % p)
            p.join()
    print("Halted")


processes = []

app = Flask(__name__)



@app.route("/")
def hello():
    return "Processes: %s" % len(processes)


@app.route("/spawn_node")
def spawn_node():
    processes.append("test")
    return "Processes: %s" % len(processes)
