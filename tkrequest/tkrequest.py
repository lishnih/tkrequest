#!/usr/bin/env python
# coding=utf-8
# Stan 2012-09-06, 2013-05-01

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, socket, webbrowser

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


py_version = sys.version_info[:2]
PY3 = py_version[0] == 3


s = Settings()
s.saveEnv()


# recipe from http://effbot.org/zone/tk-menubar.htm
class AppUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("tkRequest")

        self.Entry = None
        self.Text = None

        self.url = tk.StringVar()

        self.status = tk.StringVar()
        self.setStatus()

        self.menubar = tk.Menu(self)

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(command=self.quit, label="Exit")

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=menu)
        menu.add_command(command=self.onAbout, label="About")

        try:
            self.config(menu=self.menubar)
        except AttributeError:
            # master is a toplevel window (Python 1.4/tk 1.63)
            self.tk.call(master, "config", "-menu", self.menubar)

    def assignEntry(self, Entry):
        self.Entry = Entry

    def assignText(self, Text):
        self.Text = Text

    def setEntry(self, values_list=[]):
        self.Entry['values'] = values_list

    def setText(self, text=""):
        if self.Text:
            self.Text.delete(1.0, tk.END)
            self.Text.insert(tk.INSERT, "{0}\n".format(text))

    def setStatus(self, text=""):
        status = sys.executable
        if text:
            status += " :: " + text
        self.status.set(status)

    def onAbout(self):
        print("Version {0}".format(__VERSION__))

    def onRequest(self, event=None):
        url = self.url.get()
        urls = s.insert("urls", 0, url, 2)
        self.setEntry(urls)
        output = self.request(url, [])
        text = "\n".join(output)
        self.setText(text)

    def onOpenLink(self, event=None):
        if event.state == 4:
            url = self.url.get()
            webbrowser.open(url)
        if event.state == 0:
            wtype = event.widget.winfo_class()
            if wtype not in ['Entry', 'Text', 'TCombobox']:
                url = self.url.get()
                webbrowser.open(url)

    def request(self, url, output = [], level=0):
        output.append("=== {0} ===".format(url))

        try:
            r = urllib2.Request(url)
            page = urllib2.urlopen(r)
            output.append(r.get_method())
            output.append(r.get_type())
            for h, v in r.header_items():
                output.append("  {0}: {1}".format(h, v))
            output.append("")

        except Exception as e:
            output.append(plain(e))

        else:
            head = page.info()._headers if PY3 else page.info().headers
            output.append(plain(head))
            output.append("")

            html = page.readlines()
            for i in html:
                output.append(plain(i))
            output.append("")

            returl = page.geturl()
            if returl != url:
                if level <= 15:
                    self.request(returl, output, level+1)
                else:
                    pass

        return output


def main():
    root = AppUI()

    line1 = tk.Frame(root)
    line2 = tk.Frame(root)
    line3 = tk.Frame(root)

    # Address
    entry1 = ttk.Combobox(line1, textvariable=root.url)
    root.assignEntry(entry1)
    urls = s.get('urls', ["http://localhost:80/"])
    root.setEntry(urls)
    entry1.current(0)

    button1 = tk.Button(line1, text="Request")

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
    button1.pack(side=tk.RIGHT)

    text1.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    text1_yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    label1.pack(fill=tk.X)

    # Bind
    button1.bind("<Button-1>", root.onRequest)
    entry1.bind("<KeyPress-Return>", root.onRequest)
    root.bind("w", root.onOpenLink)

    # Main loop
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.mainloop()



if __name__ == '__main__':
    main()
