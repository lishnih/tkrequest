#!/usr/bin/env python
# coding=utf-8
# Stan 2012-09-06, 2013-05-01

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, socket, webbrowser

try:
    from .lib.info import __VERSION__
    from .lib.backwardcompat import *
    from .lib.settings import Settings
except:
    from lib.info import __VERSION__
    from lib.backwardcompat import *
    from lib.settings import Settings


py_version = sys.version_info[:2]
PY3 = py_version[0] == 3

if PY3:
    def _(msg):
        return msg
else:
    try:
        import chardet
        def _(msg):
            det = chardet.detect(msg)
            encoding = det.get('encoding')
            if encoding:
                if encoding == 'MacCyrillic':   # !!! Windows-1251 as MacCyrillic
                    encoding = 'Windows-1251'
                return msg.decode(encoding, 'replace')
            else:
                return msg
    except ImportError:
        def _(msg):
            return msg.decode('ascii', 'replace')


company_section = "lishnih@gmail.com"
s = Settings(company_section)
s.saveEnv()


# recipe from http://effbot.org/zone/tkinter-menubar.htm
class AppUI(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.title("tkRequest")

        self.Text = None
        self.Entry = None

        self.url = tkinter.StringVar()

        self.status = tkinter.StringVar()
        self.setStatus()

        self.menubar = tkinter.Menu(self)

        menu = tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=menu)
        menu.add_command(command=self.onAbout, label="About")

        try:
            self.config(menu=self.menubar)
        except AttributeError:
            # master is a toplevel window (Python 1.4/Tkinter 1.63)
            self.tk.call(master, "config", "-menu", self.menubar)

    def assignText(self, Text):
        self.Text = Text

    def assignEntry(self, Entry):
        self.Entry = Entry

    def setText(self, text=""):
        self.Text.delete(1.0, tkinter.END)
        self.Text.insert(tkinter.INSERT, "{0}\n".format(text))

    def setEntry(self, values_list=[]):
        self.Entry['values'] = values_list

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
        if event.state == 0 and event.widget != self.Text and event.widget != self.Entry:
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

        except urllib2.HTTPError as e:
            code = e.code
            msg = e.reason
            msg = _(msg)
            output.append("HTTPError [{0}]: {1}".format(code, msg))

        except urllib2.URLError as e:
            msg = e.reason

            if isinstance(msg, string_types):
                msg = _(msg)
                output.append("URLError: {0}".format(msg))
            elif isinstance(msg, socket.error):
                if PY3:
                    msg = _(msg)
                    output.append("URLError: {0}".format(msg))
                else:
                    errno, msg = msg
                    msg = _(msg)
                    output.append("URLError [{0}]: {1}".format(errno, msg))
            else:
                msg = _(msg)
                output.append("URLError: {0}".format(msg))

        except ValueError as e:
            msg = e.message

            msg = _(msg)
            output.append("ValueError: {0}".format(msg))

        else:
            head = page.info()._headers if PY3 else page.info().headers
            for i in head:
                h = ": ".join(i).rstrip() if PY3 else _(i).rstrip()
                output.append(h)
            output.append("")

#             html = page.readlines()
#             for i in html:
#                 output.append(_(i).rstrip())
#             output.append("")

            returl = page.geturl()
            if returl != url:
                if level <= 15:
                    self.request(returl, output, level+1)
                else:
                    pass

        return output


def main():
    root = AppUI()

    line1 = tkinter.Frame(root)
    line2 = tkinter.Frame(root)
    line3 = tkinter.Frame(root)

    # Address
    entry1 = ttk.Combobox(line1, textvariable=root.url)
    root.assignEntry(entry1)
    urls = s.get('urls', ["http://localhost:80/"])
    root.setEntry(urls)
    entry1.current(0)

    button1 = tkinter.Button(line1, text="Request")

    # Text Widget
    dFont1 = Font(family="Courier", size=9)
    text1 = tkinter.Text(line2, font=dFont1)
    root.assignText(text1)
    text1_yscrollbar = tkinter.Scrollbar(line2, orient=tkinter.VERTICAL, command=text1.yview)
    text1['yscrollcommand'] = text1_yscrollbar.set

    # Status
    label1 = tkinter.Label(line3, textvariable=root.status, anchor=tkinter.W)

    # Pack
    line1.pack(fill = 'x')
    line2.pack(fill = 'both', expand = 1)
    line3.pack(fill = 'x')

    entry1.pack(side = 'left', fill = 'x', expand = 1)
    button1.pack(side = 'right')

    text1.pack(side = 'left', fill = 'both', expand = 1)
    text1_yscrollbar.pack(side = 'right', fill = 'y')

    label1.pack(fill = 'x')

    # Bind
    button1.bind("<Button-1>", root.onRequest)
    entry1.bind("<KeyPress-Return>", root.onRequest)
    root.bind("<w>", root.onOpenLink)

    # Main loop
    root.mainloop()

    s.save()



if __name__ == '__main__':
    main()
