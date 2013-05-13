#!/usr/bin/env python
# coding=utf-8
# Stan 2011-07-22

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, threading, webbrowser

try:
    from .lib.info import __VERSION__
    from .lib.backwardcompat import *
    from .lib.dump import plain
    from .lib.settings import Settings
except:
    from lib.info import __VERSION__
    from lib.backwardcompat import *
    from lib.dump import plain
    from lib.settings import Settings


s = Settings()
s.saveEnv()


# recipe from http://effbot.org/zone/tk-menubar.htm
class AppUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("tkDummyServer")

        self.server = None

        self.host = tk.StringVar()
        self.port = tk.StringVar()

        self.status = tk.StringVar()
        self.setStatus()

        self.menubar = tk.Menu(self)

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=menu)
        menu.add_command(command=self.onAbout, label="About")

        try:
            self.config(menu=self.menubar)
        except AttributeError:
            # master is a toplevel window (Python 1.4/tk 1.63)
            self.tk.call(master, "config", "-menu", self.menubar)

    def assignText(self, Text):
        self.Text = Text

    def setStatus(self, text=""):
        status = sys.executable
        if text:
            status += " :: " + text
        self.status.set(status)

    def onAbout(self):
        print("Version {0}".format(__VERSION__))

    def onStartServer(self, event=None):
        if self.server is None:    
            host = self.host.get()
            port = self.port.get()
            port = int(port) if port else 80

            s.set('server_host', host)
            s.set('server_port', port)

            self.setStatus("Server started!")
            t = threading.Thread(target=self.startServer, args=(host, port))
            t.daemon = True
            t.start()
        else:            
            self.setStatus()
            self.server.shutdown()
            self.server = None                        

    def startServer(self, host, port):
        self.server = MyServer((host, port), MyHandler, self.Text)
        self.server.serve_forever()

    def onOpenLink(self, event=None):
        host = self.host.get()
        port = self.port.get()
        if port:
            port = ":" + port
        url = "http://" + host + port

        if event.state == 4:
            webbrowser.open(url)
        if event.state == 0:
            wtype = event.widget.winfo_class()
            if wtype not in ['Entry', 'Text', 'TCombobox']:
                webbrowser.open(url)


# recipe from http://www.gossamer-threads.com/lists/python/python/573423
class MyServer(SocketServer.ThreadingTCPServer): 
    def __init__(self, server_address, RequestHandlerClass, Text): 
        SocketServer.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass) 
        self.Text = Text 


class MyHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.request.send(self.data)

        text = "=== {0} ===\n{1}\n".format(self.client_address[0], u(self.data))

        if self.server.Text:
#           self.server.Text.delete(1.0, tk.END)
            self.server.Text.insert(tk.END, text)
        else:
            print(text)


def validate_port(value):
    if not value:
        return True
    if value.isdigit() and int(value) < 65536:
        return True
    return False


def main():
    root = AppUI()

    line1 = tk.Frame(root)
    line2 = tk.Frame(root)
    line3 = tk.Frame(root)

    # Host / Port
    entry1 = tk.Entry(line1, textvariable=root.host)

    vcmd = root.register(validate_port), '%P'
    entry2 = tk.Entry(line1, textvariable=root.port, validate="key", validatecommand=vcmd)

    root.host.set(s.get('server_host', 'localhost'))
    root.port.set(s.get('server_port', '80'))

    button1 = tk.Button(line1, text="Start/stop server")

    # Text Widget
    dFont1 = Font(family="Courier", size=9)
    text1 = tk.Text(line2, font=dFont1)
    root.assignText(text1)
    text1_yscrollbar = tk.Scrollbar(line2, orient=tk.VERTICAL, command=text1.yview)
    text1['yscrollcommand'] = text1_yscrollbar.set

    # Status
    label1 = tk.Label(line3, textvariable=root.status, anchor=tk.W)

    # Pack
    line1.pack(fill=tk.X)
    line2.pack(fill=tk.BOTH, expand=1)
    line3.pack(fill=tk.X)

    entry1.pack(side=tk.LEFT, fill=tk.X, expand=1)
    entry2.pack(side=tk.LEFT, fill=tk.X)
    button1.pack(side=tk.RIGHT)

    text1.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    text1_yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    label1.pack(fill=tk.X)

    # Bind
    button1.bind("<Button-1>", root.onStartServer)
    entry1.bind("<KeyPress-Return>", root.onStartServer)
    entry2.bind("<KeyPress-Return>", root.onStartServer)
    root.bind("<w>", root.onOpenLink)

    # Main loop
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.mainloop()



if __name__ == '__main__':
    main()
