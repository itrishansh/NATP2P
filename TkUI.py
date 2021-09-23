import queue
import tkinter
from tkinter import scrolledtext
from tkinter import Button

# Done: Implement Enter to send
class TkUI:
    def __init__(self, sendcb = None):
        self.sendcb = sendcb
        self.initComponents()
        self.jobs = queue.Queue()
        pass

    def setSendCb(self, sendcb):
        self.sendcb = sendcb

    def clickSend(self):
        # print("Clicked Send Button.")
        msg = self.typeBx.get(1.0, tkinter.END)
        msg = msg.rstrip()
        # print("clickSend with %s" % repr(msg))
        self.typeBx.delete(1.0, tkinter.END)
        if self.sendcb:
            # print ("calling send cb")
            self.sendcb(msg)
            # print("done with send cb")
        else:
            print("sendcb is none")
            self.appendMessage(msg)
        # self.typeBx.insert(tkinter.INSERT, "Some text")
        # self.appendMessage(msg)

    def appendMessage(self, msg: str):
        if isinstance(msg, bytes):
            msg = msg.decode().rstrip()
        if msg[-1] != '\n':
            msg = msg + '\n'
        self.msgBx.insert(tkinter.END, msg)
        self.msgBx.see(tkinter.END)

    def postJob(self, key, value):
        self.jobs.put((key, value))

    def processJobs(self):
        # print("Ui-Update called")
        while not self.jobs.empty():
            key, data = self.jobs.get()
            # print("Ui-Update", key, data)
            if key == 'append_msg':
                data = data[0] + " > " + data[1]
                self.appendMessage(data)
        # Reschedule to run after 100ms
        self.window.after(100, self.processJobs)

    def initComponents(self):
        self.window = tkinter.Tk()
        self.window.title('Test UDP punchhole')
        self.topFrame = tkinter.Frame(self.window)
        self.botFrame = tkinter.Frame(self.window)
        self.msgBx = scrolledtext.ScrolledText(self.topFrame)
        self.typeBx = scrolledtext.ScrolledText(self.botFrame, height=5)
        self.typeBx.bind("<KeyPress-Return>", self.typeBoxKeyDown)
        self.typeBx.bind("<KeyRelease-Return>", self.typeBoxKeyUp)
        self.btSend = Button(self.botFrame, text="Send", command=self.clickSend)
        self.topFrame.pack(expand=True, fill = tkinter.BOTH)
        self.botFrame.pack(side = "bottom", expand=True, fill = tkinter.BOTH)
        self.msgBx.pack(expand=True, fill = tkinter.BOTH)
        self.typeBx.pack(side = "left", expand = True, fill = tkinter.BOTH)
        self.btSend.pack(expand = True, fill = tkinter.BOTH)
        self.window.after(100, self.processJobs)

    def mainLoop(self):
        self.window.mainloop()

    def typeBoxKeyDown(self, event):
        self.clickSend()
        # print(dir(event))

    def typeBoxKeyUp(self, event):
        # print(type(event))
        # print(dir(event))
        # self.clickSend()
        self.typeBx.delete(1.0, tkinter.END)

if __name__ == '__main__':
    ui = TkUI()
    ui.mainLoop()
    print("After MainLoop")