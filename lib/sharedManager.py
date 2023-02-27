from multiprocessing import Value
from enum import IntEnum
import logging
import json

class SharedManager(object):
    class OnOffFlags(IntEnum):
        On = 1
        Off = 0

    def __init__(self):
        pass

    @classmethod
    def isDictVar(cls, d):
        return 'type' in d.keys() and not isinstance(d['type'], dict)

    def setModules(self, modules):
        self.modules = modules

    def initSharedVars(self):
        self.vars = self.getVars()
        def t(v):
            if self.isDictVar(v):
                v['shared'] = Value(v['type'], v['value'], lock=False)
            else:
                for ak, av in v.items():
                    t(av)
        t(self.vars)

    def getDisplayVars(self):
        return {}

    def getVar(self, name):
        e = self.vars
        for p in name.split('.'):
            e = e[p]
        return e

    def varExists(self, name):
        e = self.vars
        for p in name.split('.'):
            if p not in e.keys():
                return False
            e = e[p]
        return True

    def setValue(self, name, value):
        e = self.getVar(name)
        if e['type'] == 'f':
            value = float(value)
        else:
            value = int(value)
        e['shared'].value = value

    def getValue(self, name):
        return self.getVar(name)['shared'].value

    def load(self, file = None):
        def t(v, k = []):
            for ak, av in v.items():
                p = list(k)
                p.append(ak)
                if not isinstance(av, dict):
                    path = '.'.join(p)
                    if self.varExists(path):
                        self.setValue(path, av)
                else:
                    t(av, p)

        if file is None:
            file = self.file
        try:
            with open(file, 'r') as i:
                values = json.load(i)
                t(values)
        except FileNotFoundError:
            logging.debug('Config file %s does not exist' % file)

    def save(self, file = None):
        def t(v, k = []):
            values = {}
            for ak, av in v.items():
                p = list(k)
                p.append(ak)
                if self.isDictVar(av):
                    values[ak] = self.getValue('.'.join(p))
                else:
                    values[ak] = t(av, p)
            return values

        if file is None:
            file = self.file

        values = t(self.vars)
        with open(file, 'w') as o:
            json.dump(values, o, indent=4)
