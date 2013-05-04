#!/usr/bin/env python
# coding=utf-8
# Stan 2013-05-02

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import sys, os, re, time, pickle, logging

try:
    from .info import __VERSION__
except:
    from info import __VERSION__


def save_entry(filename, entry):
    with open(filename, 'wb') as f:
        pickle.dump(entry, f, 2)


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
    def __init__(self, company_section, app_section=None):
        self.home = os.path.expanduser("~")
        self.company_section = company_section
        self.app_section = app_section if app_section else \
                           re.sub(r'\W', '_', os.path.dirname(os.path.dirname(__file__)))

        configdir = os.path.join(self.home, self.company_section)
        self.filename = os.path.join(configdir, "{0}.pickle".format(self.app_section))
        self.settings = load_entry(self.filename)


    def __del__(self):
        pass


    def __iter__(self):
        for key in sorted(self.settings.keys()):
            yield key, self.settings[key]


    def save(self):
        save_entry(self.filename, self.settings)


    def contains(self, key):
        return key in self.settings


    def get(self, key, default=None):
        return self.settings.setdefault(key, default)


    def set(self, key, value):
        self.settings[key] = value


    def remove(self, key):
        if key in self.settings:
            del self.settings[key]


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
        self.set(d+"/Python", sys.version)
        self.set(d+"/Core", __VERSION__)


    def set_path(self, key, default, check=None):
        value = self.get(key)

        if not value or not isinstance(value, basestring):
            value = self.expand_path(default)
            self.set(key, value)

        if check and not self.check_path(value):
            self.remove(key)


    def expand_path(self, path):
        if path == '~':
            home = os.path.expanduser("~")
            return home
        elif path == '~~':
            home = os.path.expanduser("~")
            value = os.path.join(home, self.company_section)
            return value
        elif path == '~~~':
            home = os.path.expanduser("~")
            value = os.path.join(home, self.company_section, self.app_section)
            return value
        else:
            return path


    def check_path(self, path):
        if not os.path.exists(path):
            logging.info(u"Creating directory: {0}".format(path))
            os.makedirs(path)

        if os.path.isdir(path):
            return True
        else:
            logging.error(u"Could not create directory: {0}".format(path))
            return False


def main():
    company_section = "lishnih@gmail.com"
    s = Settings(company_section)
    s.saveEnv()

    s.set_path('companydata', '~~', True)
    s.set_path('appdata',     '~~~', True)

    for key, value in s:
        print("{0:20}{1:16}{2}".format(key, type(value), value))

    s.save()
    

if __name__ == '__main__':
    main()
