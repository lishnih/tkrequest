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


if sys.version_info >= (3,):
    basestring = str
    class aStr():
        def __str__(self):
            return self.__unicode__()
else:
    class aStr():
        def __str__(self):
            return self.__unicode__().encode('utf-8')


class aObject(object): pass


class SettingsGroup(object):
    def __init__(self, settings={}, filename=None):
        self.settings = settings
        if filename:
            self.load(filename)


    def __iter__(self):
        for key in sorted(self.settings.keys()):
            yield key, self.settings[key]


    def __str__(self):
        return self.__unicode__().encode('utf-8')


    def __unicode__(self):
        str = "{0}".format(type(self))
        for key, value in self:
            str += "\n    {0:20}: {1:16}{2}".format(key, type(value), value)
        return str


    def load(self, filename):
        self.system.filename = filename

        if not os.path.exists(filename):
            logging.warning("{0} not exists!".format(filename))
            return
        if not os.path.isfile(filename):
            logging.error("{0} must be a file!".format(filename))
            return

        try:
            with open(filename, 'rb') as f:
                self.settings = pickle.load(f)
        except Exception as e:
            logging.exception("Unable to read/parse file: {0} [{1}]".format(filename, e))


    def save(self):
        if not self.system.filename:
            logging.warning("File is not specified!")
            return

        try:
            with open(self.system.filename, 'wb') as f:
                pickle.dump(self.settings, f, 2)
        except pickle.PicklingError as e:
            logging.exception("Unable to write file: {0} [{1}]".format(self.system.filename, e))


    def get_dict(self):
        return self.settings


    def get_group(self, key):
        settings = self.get(key, {}, parse=False)
        group = SettingsGroup(settings)
        group.system = self.system
        return group


# Работа с ключами


    def contains(self, key):
        return key in self.settings


    def get(self, key, default=None, parse=True):
        value = self.settings.get(key, default)
        if parse:
            value = self.parse(value)
        return value


    def set(self, key, value):
        self.settings[key] = value
        self.system.flush()


    def set_default(self, key, default=None):
        if key not in self.settings:
            self.set(key, default)


    def remove(self, key):
        if key in self.settings:
            del self.settings[key]
            self.system.flush()


    def clean(self):
        self.settings = {}
        self.system.flush()


    def parse(self, value):
        if isinstance(value, basestring):
            res = re.match(r'(~{1,3}|\$)[\/]?(.*)', value)
            if res:
                prefix, value = res.groups()
                value = os.path.join(self.expand_prefix(prefix), value)

        return value


# Работа с ключами (списки)


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


# Работа с ключами (директории)


    def get_path(self, key, default=None, check=None):
        value = self.get(key, default)

        if check and not self.check_path(value):
            self.remove(key)
            return

        return value


    def set_path(self, key, path, check=None):
        self.set(key, path)
        if check:
            self.get_path(key, check=check)


    def expand_prefix(self, path):
        if path == '~':
            return self.system.home
        elif path == '~~':
            return os.path.join(self.system.location)
        elif path == '~~~':
            return os.path.join(self.system.path)
        elif path == '$':
            return self.system.instance


    def check_path(self, path):
        if not os.path.exists(path):
            logging.info("Creating directory: {0}".format(path))
            os.makedirs(path)

        if os.path.isdir(path):
            return True
        else:
            logging.error("Could not create directory: {0}".format(path))
            return False


# Утилиты


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


# name         - имя файла настроек
# app          - путь файла настроек
# location     - расположение директории для всех настроек
# for_instance - загружить настройки для конкретного приложения
# filename     - загружить настройки из указанного файла,
#                остальные параметры принимаются для текущего расположения
class Settings(SettingsGroup):
    def __init__(self, name=None, app=None, location=None, for_instance=False,
                 filename=None):
        self.system = aObject()
        self.system.flush = self.flush

        self.system.home = os.path.expanduser("~")

        abspath = os.path.abspath(__file__)
        self.system.instance = os.path.dirname(os.path.dirname(abspath))

        _basename = os.path.basename(self.system.instance)
        _instancename = re.sub(r'\W', '_', self.system.instance)

        self.system.location = os.path.join(self.system.home, ".config") if location is None \
            else self.expand_path(location)
        self.system.app = _basename if app is None else app
        self.system.name = _basename if name is None else name

        if for_instance:
            self.system.path = os.path.join(self.system.location, self.system.app, _instancename)
        else:
            self.system.path = os.path.join(self.system.location, self.system.app)
        self.check_path(self.system.path)

        if not filename:
            filename = os.path.join(self.system.path, "{0}.pickle".format(self.system.name))
        SettingsGroup.__init__(self, filename=filename)


    def flush(self):
        self.save()


    def get_systems(self):
        return [(i, getattr(self.system, i)) for i in dir(self.system) if i[0] != '_']

    def get_filename(self):
        return self.system.filename
