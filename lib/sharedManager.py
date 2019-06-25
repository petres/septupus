from multiprocessing import Process, Value, Array
from enum import IntEnum, auto
import logging

class SharedManager(object):
    def initVars(self):
        self.vars = self.getVars()
        
        def t(v):
            k = v.keys()
            if 'type' in k and 'value' in k:
                v['shared'] = Value(v['type'], v['value'], lock=False)
            else:
                for ak, av in v.items():
                    t(av)
        t(self.vars)

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
        self.getVar(name)['shared'].value = int(value)

    def getValue(self, name):
        return self.getVar(name)['shared'].value
