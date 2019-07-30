from multiprocessing import Process
from threading import Thread
from enum import IntEnum, auto
from .sharedManager import SharedManager
import logging
import time

class MultiManager(SharedManager):
    class ControlFlags(IntEnum):
        run = auto()
        stop = auto()
        restart = auto()

    def __init__(self, type = 'process'):
        self.type = type
        self.multi = None
        super().__init__()

    def getVars(self):
        return {
            'multi': {
                'sleep': {
                    'name': "Sleep (ms)",
                    'type': 'I', 'control': 'range',
                    'min': 0, 'max': 1000,
                    'value': 10
                },
                'flag': {
                    'type': 'I', 'control': 'radio',
                    'value': self.ControlFlags.run.value,
                    'options': {i.name: i.value for i in self.ControlFlags}
                },
            }
        }

    def isRunning(self):
        return self.multi is not None

    def start(self):
        if self.type == 'process':
            self.multi = Process(target=self.loop)
        elif self.type == 'thread':
            self.multi = Thread(target=self.loop)
        self.prepare()
        self.multi.start()

    def prepare(self):
        pass

    def stop(self, join = True):
        if self.isRunning():
            self.setValue('multi.flag', self.ControlFlags.stop)
            if join:
                self.multi.join()
                self.multi = None

    def loop(self):
        try:
            self.loopPrepare()
            while self.getValue('multi.flag') == self.ControlFlags.run:
                t0 = time.time()
                self.loopMain()
                time.sleep(max(0, t0 - time.time() + self.getValue('multi.sleep')/1000))
        except Exception as e:
            logging.exception(e)
        finally:
            self.loopCleanup()

    def loopPrepare(self):
        pass

    def loopMain(self):
        pass

    def loopCleanup(self):
        pass
