#!/usr/bin/env python
# coding=utf-8
# Stan 2013-05-02

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, os, re, time, pickle, logging

try:
    try:    from .info import __version__
    except: from info import __version__
except:
    __version__ = '<undefined>'


def save_entry(filename, entry):
    with open(filename, 'wb') as f:
        try:
            pickle.dump(entry, f, 2)
        except pickle.PicklingError as e:
            logging.error(e)


def load_entry(filename):
    entry = {}
    if os.path.exists(filename):
        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                try:
                    entry = pickle.load(f)
                except Exception as e:
                    logging.error("Unable read/parse file: {0}".format(filename))
        else:
            logging.error("{0} must be a file!".format(filename))
    return entry


class Settings(object):
    def __init__(self, name=None, app=None, location=None, for_instance=False):
        self.home = os.path.expanduser("~")

        abspath = os.path.abspath(__file__)
        self.instance = os.path.dirname(os.path.dirname(abspath))

        _basename = os.path.basename(self.instance)
        _instancename = re.sub(r'\W', '_', self.instance)

        self.location = os.path.join(self.home, ".config") if location is None \
            else self.expand_path(location)
        self.app = _basename if app is None else app
        self.name = _basename if name is None else name

        if for_instance:
            self.path = os.path.join(self.location, self.app, _instancename)
        else:
            self.path = os.path.join(self.location, self.app)
        self.check_path(self.path)
        self.filename = os.path.join(self.path, "{0}.pickle".format(self.name))
        self.settings = load_entry(self.filename)


#     def __del__(self):
#         save_entry(self.filename, self.settings)


    def __iter__(self):
        for key in sorted(self.settings.keys()):
            yield key, self.settings[key]


    def flush(self):
        save_entry(self.filename, self.settings)


    def get_dict(self):
        return self.settings


    def contains(self, key):
        return key in self.settings


    def get(self, key, default=None):
        return self.settings.setdefault(key, default)


    def set(self, key, value):
        self.settings[key] = value
        self.flush()


    def remove(self, key):
        if key in self.settings:
            del self.settings[key]
        self.flush()


    def append(self, key, value, mode=0):
        values_list = self.get(key, [])
        if mode == 0:
            values_list.append(value)
        elif mode == 1 and value not in values_list:
            values_list.append(value)
        elif mode == 2:
            if value in values_list:
                values_list.remove(value)
            values_list.append(value)
        self.set(key, values_list)

        return values_list


    def insert(self, key, seq, value, mode=0):
        values_list = self.get(key, [])
        if mode == 0:
            values_list.insert(seq, value)
        elif mode == 1 and value not in values_list:
            values_list.insert(seq, value)
        elif mode == 2:
            if value in values_list:
                values_list.remove(value)
            values_list.insert(seq, value)
        self.set(key, values_list)

        return values_list


    def saveEnv(self):
        if not self.contains("firsttime/time"):
            self.saveEnv_d("firsttime")

        self.saveEnv_d("lasttime")

        runs = self.get("runs")
        runs = runs + 1 if isinstance(runs, int) else 1
        self.set("runs", runs)


    def saveEnv_d(self, d=""):
        tt, ct = time.time(), time.ctime()
        self.set(d+"/time", tt)
        self.set(d+"/time_str", ct)
        self.set(d+"/python", sys.version)
        self.set(d+"/version", __version__)


    def init_path(self, key, default, check=None):
        value = self.get(key)

        if not value or not isinstance(value, basestring):
            value = self.expand_path(default)
            self.set(key, value)

        if check and not self.check_path(value):
            self.remove(key)    # !!!


    def set_path(self, key, path, check=None):
        value = self.expand_path(path)
        self.set(key, value)

        if check and not self.check_path(value):
            self.remove(key)    # !!!


    def expand_prefix(self, path):
        if path == '~':
            return self.home
        elif path == '~~':
            return os.path.join(self.location)
        elif path == '~~~':
            return os.path.join(self.path)
        elif path == '$':
            return self.instance


    def expand_path(self, path):
        res = re.match('(~{1,3}|\$)(.*)', path)
        if res:
            prefix, path = res.groups()
            return os.path.join(self.expand_prefix(prefix), path)
        else:
            return path


    def check_path(self, path):
        if not os.path.exists(path):
            logging.info("Creating directory: {0}".format(path))
            os.makedirs(path)

        if os.path.isdir(path):
            return True
        else:
            logging.error("Could not create directory: {0}".format(path))
            return False
