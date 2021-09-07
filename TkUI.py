import threading
import tkinter
from tkinter import scrolledtext
from tkinter import Button

# Todo: Implement Enter to send
class TkUI:
    def __init__(self, sendcb = None):
        self.sendcb = sendcb
        self.initComponents()
        pass

    def setSendCb(self, sendcb):
        self.sendcb = sendcb

    def clickSend(self):
        # print("Clicked Send Button.")
        msg = self.typeBx.get(1.0, tkinter.END)
        # print("clickSend with %s" % repr(msg))
        self.typeBx.delete(1.0, tkinter.END)
        if self.sendcb:
            self.sendcb(msg.encode())
        else:
            self.appendMessage(msg)
        #self.typeBx.insert(tkinter.INSERT, "Some text")
        #self.appendMessage(msg)

    def appendMessage(self, msg: str):
        if msg[-1] != '\n':
            msg = msg + '\n'
        self.msgBx.insert(tkinter.END, msg)
        self.msgBx.see(tkinter.END)

    def initComponents(self):
        self.window = tkinter.Tk()
        self.window.title('Test UDP punchhole')
        self.topFrame = tkinter.Frame(self.window)
        self.botFrame = tkinter.Frame(self.window)
        self.msgBx = scrolledtext.ScrolledText(self.topFrame)
        self.typeBx = scrolledtext.ScrolledText(self.botFrame, height=5)
        # self.typeBx.bind("<KeyPress>", self.typeBoxKeyDown)
        self.typeBx.bind("<KeyRelease-Return>", self.typeBoxKeyUp)
        self.btSend = Button(self.botFrame, text="Send", command=self.clickSend)
        self.topFrame.pack(expand=True, fill = tkinter.BOTH)
        self.botFrame.pack(side = "bottom", expand=True, fill = tkinter.BOTH)
        self.msgBx.pack(expand=True, fill = tkinter.BOTH)
        self.typeBx.pack(side = "left", expand = True, fill = tkinter.BOTH)
        self.btSend.pack(expand = True, fill = tkinter.BOTH)

    def mainLoop(self):
        # class Loop (threading.Thread):
        #     def __init__(self, window):
        #         threading.Thread.__init__(self)
        #         self.win = window
        #     def run(self):
        #         self.win.mainloop()
        # th = Loop(self.window)
        # th.start()
        # th = threading.Thread(target=self.window.mainloop)
        # th.daemon = True
        # th.start()
        self.window.mainloop()

    def typeBoxKeyDown(self):
        pass

    def typeBoxKeyUp(self, event):
        # print(type(event))
        # print(dir(event))
        self.clickSend()


if __name__ == '__main__':
    ui = TkUI()
    ui.mainLoop()
    print("After MainLoop")