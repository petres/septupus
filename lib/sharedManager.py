from multiprocessing import Process, Value, Array
from enum import IntEnum, auto
import logging

class SharedManager(object):
    class OnOffFlags(IntEnum):
        On = 1
        Off = 0

    @classmethod
    def isDictVar(cls, d):
        return 'type' in d.keys() and not isinstance(d['type'], dict)

    def initVars(self):
        def t(v):
            if self.isDictVar(v):
                v['shared'] = Value(v['type'], v['value'], lock=False)
            else:
                for ak, av in v.items():
                    t(av)
        self.vars = self.getVars()
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

    def load(self):
        pass

    def save(self):
        def t(v, k = []):
            values = {}
            for ak, av in v.items():
                p = list(k)
                p.append(ak)
                if self.isDictVar(av):
                    logging.debug('.'.join(p))
                    values[ak] = self.getValue('.'.join(p))
                else:
                    values[ak] = t(av, p)
            return values
        values = t(self.vars)
        # TODO SAVE
