# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import stun
import sys
import socket as sk
import urllib.parse
import urllib.request
import time

name = ''
host = '0.0.0.0'
port = 65432

def PrepareSocket():
    ss = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    ss.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
    ss.bind((host, port))
    return ss

def PrintAvailClients():
    get_url = 'https://psycox3.pythonanywhere.com/getall'
    r = urllib.request.urlopen(get_url)
    data = r.read().decode()
    print(f'clients -> {data}')
    # ToDo: don't use eval. It's security risk.
    return eval(data)

def UpdateInfo(name, port):
    data = urllib.parse.urlencode({'name': name, 'port' : str(port)})
    data = data.encode('ascii')
    add_url = 'https://psycox3.pythonanywhere.com/addinfo'
    res = urllib.request.urlopen(add_url, data)
    print(res.read())

def SendKeepAlive(skt, eip, eport):
    skt.sendto('loopback Keep-Alive'.encode(), (eip, eport))
    data, addr = skt.recvfrom(1024)
    print (f'From: {addr} -> {data.decode()}')

def usage():
    print(f'{sys.argv[0]} name')

def main():
    port = globals()['port']
    if len(sys.argv) < 3:
        usage()
        sys.exit(0)
    name = sys.argv[1]
    other = sys.argv[2]
    if len(sys.argv) >= 4:
        port = int(sys.argv[3])

    nat_type, eip, eport = stun.get_ip_info(source_ip=host, source_port=port,
                                            stun_host='stun.l.google.com', stun_port=19302)
    print(f'({host}, {port}) -> ({eip}, {eport})')
    if eport == None:
        print(f'Unable to find external Port')
        sys.exit(1)

    skt = PrepareSocket()
    #UpdateInfo(name, eport)
    availClients = {}
    while other not in availClients:
        SendKeepAlive(skt, eip, eport)
        UpdateInfo(name, eport)
        time.sleep(1)
        availClients = PrintAvailClients()

    oip, oport = availClients[other]
    try:
        oport = int(oport)
    except:
        print(f'Invalid port {oport} for {other}')
        sys.exit(2)

    print(f'Trying to connect to ({oip}, {oport})')
    counter = 0
    while counter < 20:
        skt.sendto(f'{name} says HELLO {counter}'.encode(), (oip, oport))
        data, addr = skt.recvfrom(1024)
        print (f'From: {addr} -> {data.decode()}')
        counter = counter + 1
        time.sleep(1)


    print('Exiting')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
