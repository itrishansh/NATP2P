import sys
import argparse
import asyncio
import json
import time
import threading
import urllib.parse
import urllib.request

try:
    from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
    from aiortc.contrib.signaling import BYE
except:
    print("Please install aiortc")
    print("pip install aiortc")
    sys.exit(1)

from TkUI import TkUI

def object_to_string(obj):
    if isinstance(obj, RTCSessionDescription):
        message = {"sdp": obj.sdp, "type": obj.type}
    else:
        assert obj is BYE
        message = {"type": "bye"}
    return json.dumps(message, sort_keys=True)

def object_from_string(message_str):
    message = json.loads(message_str)
    if message["type"] in ["answer", "offer"]:
        return RTCSessionDescription(**message)
    elif message["type"] == "bye":
        return BYE

class HTTPLongPollSignalling:
    get_url = 'https://psycox3.pythonanywhere.com/RTC/get'
    clear_url = 'https://psycox3.pythonanywhere.com/RTC/clear'
    add_url = 'https://psycox3.pythonanywhere.com/RTC/addinfo'

    def __init__(self, sname, oname):
        self.sname = sname
        self.oname = oname

    def clearAllSDP(self):
        urllib.request.urlopen(HTTPLongPollSignalling.clear_url)

    def updateSDP(self, sdp):
        self.clearAllSDP()
        data = urllib.parse.urlencode({'sname': self.sname, 'oname': self.oname,
                                       'data' : sdp})
        data = data.encode('ascii')
        #print(data)
        res = urllib.request.urlopen(HTTPLongPollSignalling.add_url, data)
        #print(res.read().decode())

    async def getRemoteSDP(self):
        while True:
            data = urllib.parse.urlencode({'sname': self.sname, 'oname': self.oname})
            data = data.encode('ascii')
            res = urllib.request.urlopen(HTTPLongPollSignalling.get_url, data)
            data = res.read().decode()
            if data != "":
                print("getRemoteSDP >", data)
                return data
            time.sleep(1)

ui = None
time_start = None
def current_stamp():
    global time_start

    if time_start is None:
        time_start = time.time()
        return 0
    else:
        return int((time.time() - time_start) * 1000000)

def channel_send(channel, message):
    print(channel.label, ">", message)
    channel.send(message)

async def run_server(sname, oname):
    signalling = HTTPLongPollSignalling(sname, oname)
    pc = RTCPeerConnection()
    chat = pc.createDataChannel("chat")
    print("Creating channel", chat.label)
    pch = pc.createDataChannel("ping")
    print("Creating channel", pch.label)

    signalling.clearAllSDP()
    print("Waiting for client")

    async def send_pings():
        while True:
            channel_send(pch, "ping %d" % current_stamp())
            await asyncio.sleep(1)

    @pch.on("open")
    def on_open():
        print("channel ping opened")
        asyncio.ensure_future(send_pings())

    @pch.on("message")
    def on_message(message):
        print(pch.label, "(ping) <", message)

        if isinstance(message, str) and message.startswith("pong"):
            elapsed_ms = (current_stamp() - int(message[5:])) / 1000
            print(" RTT %.2f ms" % elapsed_ms)

    @chat.on("open")
    def on_chat_connect():
        ui.setSendCb(chat.send)
        chat.send("Channel established: Chat")
        ui.postJob('append_msg', "Channel established: Chat")


    @chat.on("message")
    def on_chat_msg(msg):
        print(chat.label, "(chat) >", msg)
        ui.postJob('append_msg', (oname, msg))
        print(chat.label, "msg added")

    await pc.setLocalDescription(await pc.createOffer())
    signalling.updateSDP(object_to_string(pc.localDescription))
    data = await signalling.getRemoteSDP()
    obj = object_from_string(data)
    await pc.setRemoteDescription(obj)

    #ui.mainLoop()
    while True:
        await asyncio.sleep(1)

async def run_client(sname, oname):
    signalling = HTTPLongPollSignalling(sname, oname)
    pc = RTCPeerConnection()

    @pc.on("datachannel")
    def on_datachannel(channel):
        print(channel.label, "-", "created by remote party")

        if channel.label == 'ping':
            @channel.on("message")
            def on_message(message):
                print(channel.label, "<", message)

                if isinstance(message, str) and message.startswith("ping"):
                    # reply
                    channel_send(channel, "pong" + message[4:])
        elif channel.label == 'chat':
            print ("Seting cb on channel chat")
            ui.setSendCb(lambda msg:(
                                        print("calling send on ch", channel.label, "with", repr(msg)),
                                        channel.send(msg)))
            @channel.on("message")
            def on_chat_msg(msg):
                print(channel.label, ">", repr(msg))
                ui.postJob("append_msg", (oname, msg))

            print("Seting cb on channel chat DONE")

    #data = input("Please enter SDP from server: ")
    data = await signalling.getRemoteSDP()
    obj = object_from_string(data)
    #print("==================")
    await pc.setRemoteDescription(obj)
    await pc.setLocalDescription(await pc.createAnswer())
    signalling.updateSDP(object_to_string(pc.localDescription))
    #print(object_to_string(pc.localDescription))

    #ui.mainLoop()
    while True:
        await asyncio.sleep(1)

def UiThread():
    global ui
    ui = TkUI()
    ui.mainLoop()

def run_async(args):
    if args.role == "server":
        coro = run_server(args.own_name, args.peer_name)
    else:
        coro = run_client(args.own_name, args.peer_name)

    # run event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coro)
    except KeyboardInterrupt:
        pass

def main():
    parser = argparse.ArgumentParser(description="Data channels ping/pong")
    parser.add_argument("role", choices=["server", "client"])
    parser.add_argument("own_name")
    parser.add_argument("peer_name")

    args = parser.parse_args()

    print(args)
    #threading.Thread(target=UiThread, daemon=True).start()
    threading.Thread(target=run_async, args=(args,), daemon=True).start()
    UiThread()
    print("Exiting")

if __name__ == "__main__":
    main()