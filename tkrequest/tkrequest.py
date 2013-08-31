#!/usr/bin/env python
# coding=utf-8
# Stan 2012-09-06

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, socket, webbrowser, logging

try:
    from .lib.info import __pkgname__, __description__, __version__
    from .lib.backwardcompat import *
    from .lib.dump import plain
    from .lib.settings import Settings
except:
    from lib.info import __pkgname__, __description__, __version__
    from lib.backwardcompat import *
    from lib.dump import plain
    from lib.settings import Settings


py_version = sys.version_info[:2]
PY3 = py_version[0] == 3


s = Settings()
s.saveEnv()


class ScrolledText(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)

        self.text = tk.Text(self, relief=tk.SUNKEN)
        self.text.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.YES)

        sbar = tk.Scrollbar(self)
        sbar.pack(fill=tk.Y, side=tk.RIGHT)
        sbar.config(command=self.text.yview)

        self.text.config(yscrollcommand=sbar.set)
        self.text.config(font=('Courier', 9, 'normal'))

    def appendText(self, text=""):
        self.text.insert(tk.END, text)
#       self.text.mark_set(tk.INSERT, "1.0")
        self.text.focus()

    def setText(self, text=""):
        self.text.delete(1.0, tk.END)
        self.appendText(text)

    def getText(self):
        return self.text.get("1.0", tk.END+'-1c')

    def bind(self, event, handler, add=None):
        self.text.bind(event, handler, add)


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
        self.title("tkRequest")

        ### Vars ###

        self.url = tk.StringVar()

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

        # Address and button
        line1 = tk.Frame(self)

        self.entry = ttk.Combobox(line1, textvariable=self.url)
        urls = s.get('urls', ["http://localhost:80/"])
        self.setEntry(urls)
        self.entry.current(0)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=1)

        button1 = tk.Button(line1, text="Request")
        button1.pack(side=tk.RIGHT)

        line1.pack(fill=tk.X)

        # Text Widget
        self.text = ScrolledText(self)
        self.text.pack(fill=tk.BOTH, expand=tk.YES)

        # Status
        self.status = StatusBar(self)
        self.status.pack(fill=tk.X)

        ### Bind ###

        button1.bind("<Button-1>", self.onRequest)
        self.entry.bind("<KeyPress-Return>", self.onRequest)
        self.bind("w", self.onOpenLink)

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
        url = self.url.get()
        urls = s.insert("urls", 0, url, 2)
        self.setEntry(urls)

        self.text.setText()
        self.text.text.tag_config("url", background="yellow", foreground="blue")

        for url, output in self.request(url):
            start = self.text.text.index(tk.CURRENT)
            self.text.appendText(url)
            stop = self.text.text.index(tk.CURRENT)
            self.text.text.tag_add("url", start, stop)

            text = "\n".join(output)
            self.text.appendText("\n"+text)

    def onOpenLink(self, event=None):
        url = self.url.get()

        if event.state == 4:
            webbrowser.open(url)
        if event.state == 0:
            wtype = event.widget.winfo_class()
            if wtype not in ['Entry', 'Text', 'TCombobox']:
                webbrowser.open(url)

    ### Functions ###

    def setEntry(self, values_list=[]):
        self.entry['values'] = values_list

    def request(self, url, level=0):
        logging.debug(url)
        output = [""]

        if level > 15:
            output.append("*** break ***")
            yield url, output

        try:
            r = urllib2.Request(url)
            page = urllib2.urlopen(r)
            output.append(r.get_method())
            output.append(plain(r))
            output.append("")

        except Exception as e:
            output.append(plain(e))
            yield url, output

        else:
            head = page.info()._headers if PY3 else \
                   page.info().headers
            output.append(plain(head))
            output.append("")

            html = page.readlines()
            for i in html:
                output.append(plain(i))
            output.append("")
            output.append("")

            yield url, output

            returl = page.geturl()
            if returl != url:
                logging.debug("Redirecting: {0}".format(returl))
                for x in self.request(returl, level+1):
                    yield x



def main():
    root = AppUI()

    root.mainloop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    main()
