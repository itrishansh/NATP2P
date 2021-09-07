import sys
import socket as sk
import urllib.parse
import urllib.request
import time
import threading

try:
    import stun
except:
    print('Install stun with')
    print('pip install pystun3')
    sys.exit(1)

class P2PUDPSocket:
    get_url = 'https://psycox3.pythonanywhere.com/getall'
    clear_url = 'https://psycox3.pythonanywhere.com/clear'
    add_url = 'https://psycox3.pythonanywhere.com/addinfo'
    DEINIT = 0
    CONNECTING = 1
    CONNECTED = 2
    def __init__(self, me, other, logger, local_port=65432, stun_host='stun.l.google.com', stun_port=19302):
        self.me = me
        self.other = other
        self.logger = logger
        self.stun_host = stun_host
        self.stun_port = stun_port
        self.lport = local_port
        self.lhost = '0.0.0.0'
        self.eip = None
        self.eport = None
        self.ss = None
        self.oip = None
        self.oport = None
        self.recvTh = None
        self.termRecvTh = False
        self.state = P2PUDPSocket.DEINIT

    def connect(self):
        nat_type, eip, eport = stun.get_ip_info(source_ip=self.lhost, source_port=self.lport,
                                            stun_host=self.stun_host, stun_port=self.stun_port)
        #print(type(self.logger))
        self.logger(f'{nat_type}')
        self.logger(f'({self.lhost}, {self.lport}) -> ({eip}, {eport})')

        if eport is None:
            self.logger(f'Unable to find external Port')
            return None

        self.eip = eip
        self.eport = eport

        self.ss = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.ss.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
        self.ss.bind((self.lhost, self.lport))

        self.clearServerCache()
        availClients = {}
        while self.other not in availClients:
            self.SendKeepAlive()
            self.UpdateInfo()
            time.sleep(1)
            availClients = self.getAvailClients()

        self.oip, self.oport = availClients[self.other]

        try:
            self.oport = int(self.oport)
        except:
            self.logger(f'Invalid port {self.oport} for {self.other}')
            return None

        self.logger(f'Starting recv thread')
        self.startRecv()

        self.logger(f'Trying to connect to ({self.oip}, {self.oport})')
        counter = 0
        while counter < 6:
            msg = f'{self.me} says HELLO {counter}'.encode()
            self.logger(f"Sending {msg}")
            self.ss.sendto(msg, (self.oip, self.oport))
            #data, addr = self.ss.recvfrom(1024)
            #self.logger(f'From: {addr} -> {data.decode()}')
            counter = counter + 1
            time.sleep(1)

        self.logger('Exiting')

    def __recvLoop(self):
        helo_msg = f'{self.other} says HELLO '
        while self.termRecvTh:
            data, addr = self.ss.recvfrom(1024)
            data = data.decode()
            self.logger(f'From: {addr} -> {data}')
            if data.startswith(helo_msg):
                self.state = P2PUDPSocket.CONNECTED

    def startRecv(self):
        self.recvTh = threading.Thread(target=self.__recvLoop, daemon=True)
        self.termRecvTh = True
        self.recvTh.start()

    def clearServerCache(self):
        r = urllib.request.urlopen(P2PUDPSocket.clear_url)

    def getAvailClients(self):
        r = urllib.request.urlopen(P2PUDPSocket.get_url)
        data = r.read().decode()
        self.logger(f'clients -> {data}')
        # ToDo: don't use eval. It's security risk.
        return eval(data)

    def UpdateInfo(self):
        data = urllib.parse.urlencode({'name': self.me, 'port': str(self.lport)})
        data = data.encode('ascii')
        #add_url = 'https://psycox3.pythonanywhere.com/addinfo'
        res = urllib.request.urlopen(P2PUDPSocket.add_url, data)
        self.logger(res.read().decode())

    def SendKeepAlive(self):
        self.ss.sendto('loopback Keep-Alive'.encode(), (self.eip, self.eport))
        data, addr = self.ss.recvfrom(1024)
        self.logger(f'From: {addr} -> {data.decode()}')

    def sendBytes(self, data: bytes):
        self.ss.sendto(data, (self.oip, self.oport))

    def disconnect(self):
        self.termRecvTh = False
        # self.recvTh.join()
