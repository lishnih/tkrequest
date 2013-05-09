#!/usr/bin/env python
# coding=utf-8
# Stan 2013-05-09

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

try:
    from .dump import *
except:
    from dump import *


class propertyDialog(tk.Toplevel):
    def __init__(self, _dict):
        tk.Toplevel.__init__(self)
        self.title("Property")

        frame = ttk.Frame(self, padding="3")
        frame.pack(fill=tk.BOTH, expand=1)

        self.tree = ttk.Treeview(frame, columns=('Types', 'Values', 'iid'))
        self.tree.heading('#0', text='Key')
        self.tree.heading('Types', text='Type')
        self.tree.heading('Values', text='Value')
        self.tree.heading('iid', text='iid')
        self.tree.column('#0', minwidth=50, width=150, stretch=False)
        self.tree.column('Types', minwidth=50, width=100, stretch=False, anchor='center')
        self.tree.column('Values')
        self.tree.column('iid', minwidth=50, width=100, stretch=False, anchor='center')

#       self.tree.bind('<Double-1>', edit_cell)
        self.tree.pack(fill=tk.BOTH, expand=1)

        self.buildTree(_dict)

        self.update_idletasks()
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())


    def escape(self, value):
        if isinstance(value, string_types):
            value = value.replace('\\', '\\\\')
        return value


    def buildTree(self, obj, name='root', parent=''):
        item = self.tree.insert(parent, 'end')

        if obj is None:
            value = plain_type(obj), "None", item
            self.tree.item(item, text=name, value=value, tags = ('none',))
            return

        if isinstance(obj, simple_types):
            value = plain_type(obj), self.escape(plain(obj)), item
            self.tree.item(item, text=name, value=value)
            return

        value = plain_type(obj), "", item
        self.tree.item(item, text=name, value=value, tags = ('self.tree',))
        if not parent:
            self.tree.tag_configure('none', background="Gray")
            self.tree.tag_configure('self.tree', background="Lightgrey")
            self.tree.item(item, open=1)

        if isinstance(obj, collections_types):
            i = 0
            for key in obj:
                value = obj[i]
                self.buildTree(value, i, item)
                i += 1
            return

        if isinstance(obj, dict):
            for key in sorted(obj):
                value = obj[key]
                self.buildTree(value, key, item)
            return
