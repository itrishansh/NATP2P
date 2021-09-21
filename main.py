# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# install with
# pip install pystun3
import sys
import socket as sk
import urllib.parse
import urllib.request
import time
import threading

try:
    import stun
except:
    print("Install stun with")
    print('pip install pystun3')
    sys.exit(1)

from P2PUDPSocket import P2PUDPSocket
from TkUI import TkUI

port = 65432

def socketConnect(skt):
    skt.connect()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()
        sys.exit(0)
    name = sys.argv[1]
    other = sys.argv[2]
    if len(sys.argv) >= 4:
        port = int(sys.argv[3])

    ui = TkUI()
    skt = P2PUDPSocket(name, other, local_port=port, logger=ui.appendMessage)
    skTh = threading.Thread(target=socketConnect, args=(skt,), daemon=True)
    skTh.start()
    ui.setSendCb(skt.sendBytes)
    ui.mainLoop()


