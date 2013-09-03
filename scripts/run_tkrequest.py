#!/usr/bin/env python
# coding=utf-8
# Stan 2013-04-24

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import importlib, multiprocessing, logging

from tkrequest.lib.info import __pkgname__, __description__, __version__
from tkrequest.lib.backwardcompat import *


class StatusBar(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)

        self.labels = {}

    def setLabel(self, name=0, side=tk.LEFT, **kargs):
        label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W, **kargs)
        label.pack(side=side)
        self.labels[name] = label

        return label

    def setText(self, text="", name=0):
        if name in self.labels:
            label = self.labels[name]
        else:
            label = self.setLabel(name)
            self.labels[name] = label

        status = sys.executable
        if text:
            status += " :: " + text
        label.config(text=status)


class AppUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("tkRequest Panel")

        ### Menu ###

        self.menubar = tk.Menu(self)

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(command=self.quit, label="Exit")

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=menu)
        menu.add_command(command=self.onHelpAbout, label="About")

        self.config(menu=self.menubar)

        ### Widgets ###

        # Button / Bind
        line1 = tk.Frame(self)

        button = tk.Button(line1, text="Url Request")
        button.pack()
        button.bind("<Button-1>", self.onRequest)

        button = tk.Button(line1, text="Dummy Server")
        button.pack()
        button.bind("<Button-1>", self.onDummyServer)

        button = tk.Button(line1, text="View Settings")
        button.pack()
        button.bind("<Button-1>", self.onSettings)

        line1.pack(fill=tk.BOTH, expand=tk.YES)

        # Status
        self.status = StatusBar(self)
        self.status.pack(fill=tk.X)

        ### Initial ###

        self.status.setText()

        self.update_idletasks()
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())

    ### Events ###

    def onHelpAbout(self, event=None):
        text = """{0}\n{1}\nVersion {2}\n
Python: {3}
Package: {4}
""".format(__pkgname__, __description__, __version__,
           sys.version, __package__)
        showinfo("About", text)

    def onRequest(self, event=None):
        script = "tkrequest"
        self.run(script)

    def onDummyServer(self, event=None):
        script = "dummy_server"
        self.run(script)

    def onSettings(self, event=None):
        script = "tksettings"
        self.run(script)

    ### Functions ###

    def run(self, script):
        try:
            module = importlib.import_module(".{0}".format(script), 'tkrequest')
        except Exception as e:
            module = None
            logging.exception(e)

        if module:
            p = multiprocessing.Process(target=module.main)
            p.start()
            p.join()



def main():
    root = AppUI()

    root.mainloop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    main()
