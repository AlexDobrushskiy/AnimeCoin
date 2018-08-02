from flask import Flask, request, redirect, render_template


class RPC:
    pass


rpc = RPC()
app = Flask(__name__)


@app.route("/", methods=['GET'])
def index():
    processes = rpc.get_processes()
    return render_template("index.tpl", processes=processes)


@app.route("/spawn_node", methods=['POST'])
def spawn_node():
    rpc.spawn_node()
    return redirect("/")


@app.route("/kill_node", methods=['POST'])
def kill_node():
    rpc.kill_node()
    return redirect("/")


# import zerorpc
# import logging
# import time
#
# from multiprocessing import Process
# from dht_prototype.kademlia_module.kademlia_core import Kademlia
#
# BASEPORT = 12345
#
# # setting up logging
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# # TODO: hack, we have to emit a log message for this to work in the kamelia module, no idea why
# logging.info("HI")
#
#
# def run_kademlia_node(nodename, portnum, bootstrap=None):
#     k = Kademlia(nodename, portnum, bootstrap=bootstrap)
#     time.sleep(1)
#     k.set(str(nodename), "%s hello" % nodename)
#     k.run_forever()
#
#
# class Context:
#     def __init__(self):
#         self.processes = {}
#         self.processid = 0
#
#     def spawn_node(self):
#         if len(self.processes) == 0:
#             nodename, portnum, bootstrap = str(self.processid), BASEPORT, None
#         else:
#             nodename, portnum, bootstrap = str(self.processid), BASEPORT + self.processid, ("127.0.0.1", BASEPORT)
#
#         print("Starting nodename: %s, port: %s, bootstrap: %s" % (nodename, portnum, bootstrap))
#         p = Process(target=run_kademlia_node, args=(nodename, portnum, bootstrap))
#         p.start()
#
#         self.processes[self.processid] = p
#         self.processid += 1
#
#     def kill_node(self, processid):
#         if processid not in self.processes:
#             return "ERROR: No such process: %s" % processid
#
#         p = self.processes.pop(processid)
#         p.terminate()
#         p.join()
