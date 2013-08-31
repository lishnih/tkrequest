#!/usr/bin/env python
# coding=utf-8
# Stan 2013-05-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

try:
    from .lib.backwardcompat import *
    from .lib.info import __pkgname__, __description__, __version__
    from .lib.dump import plain
    from .lib.settings import Settings
    from .lib.tkprop import propertyDialog
except:
    from lib.backwardcompat import *
    from lib.info import __pkgname__, __description__, __version__
    from lib.dump import plain
    from lib.settings import Settings
    from lib.tkprop import propertyDialog

import sys, os, glob, importlib, logging


def import_file(filename):
    dirname, basename = os.path.split(filename)
    sys.path.insert(0, dirname)

    root, ext = os.path.splitext(basename)
    try:
        module = importlib.import_module(root)
    except Exception as e:
        module = None
        logging.exception(e)

    del sys.path[0]
    return module


class AppUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("tkSettings")

        ### Menu ###

        self.menubar = tk.Menu(self)

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(command=self.onLoadDefault, label="Load default")
        menu.add_command(command=self.onLoadFile, label="Load file")
        menu.add_separator()
        menu.add_command(command=self.quit, label="Exit")

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=menu)
        menu.add_command(command=self.onCleanData, label="Clean data")

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Batch import", menu=menu)
        menu.add_command(command=self.onBatch1, label="File to file")

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=menu)
        menu.add_command(command=self.onAbout, label="About")

        self.config(menu=self.menubar)

        ### Widgets ###

        # Frame with Buttons
        self.frame1 = tk.Frame(self)

        button = tk.Button(self.frame1, text="Settings")
        button.pack()
        button.bind("<Button-1>", self.onShowSettings)

        button = tk.Button(self.frame1, text="Save test data")
        button.pack()
        button.bind("<Button-1>", self.onSaveTestData)

        button = tk.Button(self.frame1, text="Import from module")
        button.pack()
        button.bind("<Button-1>", self.onImportFromModule)

        button = tk.Button(self.frame1, text="Import from module to branch")
        button.pack()
        button.bind("<Button-1>", self.onImportFromModuleToBranch)

        button = tk.Button(self.frame1, text="Import from dir")
        button.pack()
        button.bind("<Button-1>", self.onImportFromDir)

        button = tk.Button(self.frame1, text="Import from dir to branch")
        button.pack()
        button.bind("<Button-1>", self.onImportFromDirToBranch)

        # Text Widget
        dFont1 = Font(family="Courier", size=9)
        self.text1 = tk.Text(self, font=dFont1)
        self.text1_y = tk.Scrollbar(self, orient=tk.VERTICAL,
                                    command=self.text1.yview)
        self.text1['yscrollcommand'] = self.text1_y.set

        # Status Widget
        self.status = tk.StringVar()
        label1 = tk.Label(self, textvariable=self.status, anchor=tk.W)
        self.setStatus()

        ### Grid widgets ###

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1, minsize=120)
        self.grid_columnconfigure(1, weight=5, minsize=400)
        self.grid_columnconfigure(2)

        self.frame1.grid(row=0, column=0, sticky='nwes')
        self.text1.grid(row=0, column=1, sticky='nwes')
        self.text1_y.grid(row=0, column=2, sticky='nwes')

        self.grid_rowconfigure(1)
        label1.grid(row=1, column=0, columnspan=4, sticky='nwes')

        ### Initial ###

        self.onLoadDefault()

    def appendText(self, text=""):
        self.text1.insert(tk.INSERT, "{0}\n".format(plain(text)))

    def setText(self, text=""):
        self.text1.delete(1.0, tk.END)
        self.appendText(text)

    def setStatus(self, text=""):
        status = sys.executable
        if text:
            status += " :: " + text
        self.status.set(status)

    def showInfo(self):
        self.setText("System:")
        self.appendText(self.s.get_systems())
        self.appendText("Settings:")
        self.appendText(self.s.get_dict())
        self.setStatus(self.s.get_filename())

    ### From menu ###

    def onAbout(self):
        text = """{0}\n{1}\nVersion {2}\n
Python: {3}
Package: {4}
""".format(__pkgname__, __description__, __version__,
           sys.version, __package__)
        showinfo("About", text)

    def onLoadDefault(self):
        self.s = Settings()
        self.showInfo()

    def onLoadFile(self):
        initialdir = os.path.expanduser("~")
        filename = askopenfilename(initialdir=initialdir, filetypes=[
                       ('Config files', '*.pickle'),
                       ('All files', '*.*'),
                   ])
        if filename:
            self.s = Settings(filename=filename)
            self.showInfo()

    def onCleanData(self):
        response = askquestion("Clean data", "Are you sure you want to "
                   "permanently delete all information from the config?")
        if response == 'yes':
            self.s.clean()
            self.showInfo()

    def onBatch1(self):
        dfilename = askdirectory()
        if dfilename:

            pickles = []
            for filename in glob.glob(os.path.join(dfilename, '*.py')):
                module = import_file(filename)
                if module:
                    basename = os.path.basename(filename)
                    root, ext = os.path.splitext(basename)
                    logging.debug(root)
                    BRANCH = Settings(root)
                    pickles.append(BRANCH.get_filename())

                    for i in dir(module):
                        if i[0] != '_':
                            value = getattr(module, i)
                            if isinstance(value, all_types):
                                BRANCH.set(i, value)

            message = "Processed pickles:\n" + plain(pickles) + "\n\n" +\
                      "Note: Empty pickles was not created!"
            showinfo("Info", message)
            self.setText()
            self.setStatus()

    ### From buttons ###

    def onShowSettings(self, event):
        propertyDialog(self.s.get_dict())

    def onSaveTestData(self, event):
        self.s.saveEnv()
        self.s.set_path('test_instance', '$')
        self.s.set_path('test_home',     '~')
        self.s.set_path('test_location', '~~',  True)
        self.s.set_path('test_app',      '~~~', True)
        self.showInfo()

    def onImportFromModuleToBranch(self, event):
        self.onImportFromModule(event, tobranch=True)

    def onImportFromModule(self, event, tobranch=False):
        filename = askopenfilename(filetypes=[
                       ('Python files', '*.py'),
                       ('All files', '*.*'),
                   ])
        if filename:
            module = import_file(filename)
            if module:
                if tobranch:
                    branch = module.__name__
                    BRANCH = self.s.get_group(branch)
                else:
                    BRANCH = self.s

                for i in dir(module):
                    if i[0] != '_':
                        value = getattr(module, i)
                        if isinstance(value, all_types):
                            BRANCH.set(i, value)

                self.showInfo()

    def onImportFromDirToBranch(self, event):
        self.onImportFromDir(event, tobranch=True)

    def onImportFromDir(self, event, tobranch=False):
        dfilename = askdirectory()
        if dfilename:
            basename = os.path.basename(dfilename)
            logging.debug(basename)
            ROOT = self.s   # Settings(basename)

            for filename in glob.glob(os.path.join(dfilename, '*.py')):
                module = import_file(filename)
                if module:
                    if tobranch:
                        branch = module.__name__
                        BRANCH = self.s.get_group(branch)
                    else:
                        BRANCH = self.s

                    for i in dir(module):
                        if i[0] != '_':
                            value = getattr(module, i)
                            if isinstance(value, all_types):
                                BRANCH.set(i, value)

            self.showInfo()


def main():
    root = AppUI()
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.mainloop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    main()
