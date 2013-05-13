#!/usr/bin/env python
# coding=utf-8
# Stan 2013-05-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )


try:
    from .lib.backwardcompat import *
    from .lib.settings import Settings
    from .lib.tkprop import propertyDialog
except:
    from lib.backwardcompat import *
    from lib.settings import Settings
    from lib.tkprop import propertyDialog


s = Settings()
s.saveEnv()


def view_plain(s):
    for i in [
        'home',
        'instance',
        'location',
        'app',
        'name',
        'path',
        'filename',
    ]:
        print("{0:20}: {1}".format(i, getattr(s, i)))

    print()

    s.set_path('home',     '~',   True)
    s.set_path('location', '~~',  True)
    s.set_path('app',      '~~~', True)
    s.set_path('instance', '$')

    for key, value in s:
        print("{0:20}: {1:16}{2}".format(key, type(value), value))


def onShowSettings(event):
    propertyDialog(s.get_dict())


def view_gui(s):
    root = tk.Tk()

    button1 = tk.Button(root, text="Settings")
    button1.pack()
    button1.bind("<Button-1>", onShowSettings)

    # Main loop
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.mainloop()


def main():
    view_plain(s)
    view_gui(s)


if __name__ == '__main__':
    main()
