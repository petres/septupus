from multiprocessing import Process, Value, Array
from enum import IntEnum, auto
import logging

class ProcessManager(object):
    class ControlFlags(IntEnum):
        run = auto()
        stop = auto()
        restart = auto()

    def __init__(self):
        self.process = None

    def isRunning(self):
        return self.process is not None

    def startProcess(self):
        self.prepareProcess()

        self.process = Process(target=self.loop)
        self.process.start()

    def prepareProcess(self):
        pass

    def stopProcess(self, join = True):
        if self.isRunning():
            self.setValue('control.flag', self.ControlFlags.stop)
            if join:
                self.process.join()
                self.process = None

    def loop(self):
        try:
            self.loopStart()
            while self.getValue('control.flag') == self.ControlFlags.run:
                self.loopMain()
        except Exception as e:
            logging.exception(e)
        finally:
            self.loopEnd()

    def loopStart(self):
        pass

    def loopMain(self):
        pass

    def loopEnd(self):
        pass
