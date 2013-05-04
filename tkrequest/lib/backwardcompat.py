#!/usr/bin/env python
# coding=utf-8
# Stan 2013-04-22

"""Stuff that differs in different Python versions"""

import sys


console_encoding = sys.__stdout__.encoding

if sys.version_info >= (3,):
    from urllib.error import URLError, HTTPError
    from queue import Queue, Empty
    from urllib.request import url2pathname
    from urllib.request import urlretrieve
    from email import message as emailmessage
    import urllib.parse as urllib
    import urllib.request as urllib2
    import urllib.parse as urlparse
    import configparser as ConfigParser
    import xmlrpc.client as xmlrpclib
    import http.client as httplib

    from tkinter import ttk
    import tkinter
    from tkinter.font import Font
    from tkinter.filedialog import askopenfilename, asksaveasfilename

    def cmp(a, b):
        return (a > b) - (a < b)

    def b(s):
        return s.encode('utf-8')

    def u(s):
        return s.decode('utf-8')

    def console_to_str(s):
        try:
            return s.decode(console_encoding)
        except UnicodeDecodeError:
            return s.decode('utf_8')

    def fwrite(f, s):
        f.buffer.write(b(s))

    bytes = bytes
    unicode = str
    string_types = (str,)

else:
    from urllib2 import URLError, HTTPError
    from Queue import Queue, Empty
    from urllib import url2pathname, urlretrieve
    from email import Message as emailmessage
    import urllib
    import urllib2
    import urlparse
    import ConfigParser
    import xmlrpclib
    import httplib

    import ttk
    import Tkinter as tkinter
    from tkFont import Font
    from tkFileDialog import askopenfilename, asksaveasfilename

    def b(s):
        return s

    def u(s):
        return s

    def console_to_str(s):
        return s

    def fwrite(f, s):
        f.write(s)

    bytes = str
    unicode = unicode
    string_types = (basestring,)
    cmp = cmp
