# -*- coding: utf-8 -*-

import logging
import sys

from dht_prototype.masternode_modules.animecoin_modules.animecoin_keys import animecoin_id_keypair_generation_func
from dht_prototype.masternode_modules.masternode_communication import NodeManager
from dht_prototype.masternode_modules.masternode_discovery import discover_nodes

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtQuick import QQuickItem
from PyQt5.QtQml import QQmlApplicationEngine, QQmlComponent


def initlogging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(' %(asctime)s - ' + __name__ + ' - %(levelname)s - %(message)s')
    consolehandler = logging.StreamHandler()
    consolehandler.setFormatter(formatter)
    logger.addHandler(consolehandler)
    return logger


if __name__ == "__main__":
    basedir = sys.argv[2]

    # discover animecoin nodes
    logger = initlogging()

    privkey, pubkey = animecoin_id_keypair_generation_func()
    nodemanager = NodeManager(logger, privkey, pubkey)
    for settings in discover_nodes(basedir):
        nodemanager.add_masternode(settings["nodeid"], settings["ip"], settings["pyrpcport"], settings["pubkey"])

    # start GUI
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine('app.qml')

    window = engine.rootObjects()[0]

    tabs = window.findChildren(QQuickItem, "tabs", Qt.FindChildrenRecursively)[0]

    # perpare component to be added to tabs
    component = QQmlComponent(engine, None)
    component.loadUrl(QUrl("component.qml"))

    # load tabs for masternodes
    for settings in discover_nodes(basedir):
        url = "http://%s:%s@%s:%s" % (settings["rpcuser"], settings["rpcpassword"], settings["ip"], settings["pyhttpadmin"])
        print(url)
        tabs.addTab(settings["nodename"], component)

    sys.exit(app.exec_())
