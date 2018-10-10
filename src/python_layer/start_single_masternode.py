import os
import sys

from masternode_prototype.masternode_daemon import MasterNodeDaemon
from core_modules.masternode_discovery import read_settings_file

if __name__ == "__main__":
    basedir = sys.argv[1]
    nodes = None
    if len(sys.argv) > 2:
        nodes = [sys.argv[2]]

    cdaemon_conf = os.path.join(basedir, "animcoin.conf")
    settings = read_settings_file(basedir)
    mnd = MasterNodeDaemon(settings=settings, addnodes=nodes)
    mnd.run_event_loop()
