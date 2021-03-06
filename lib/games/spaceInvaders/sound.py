import wave
import threading
import pyaudio
import os
from .config import config

class Sound(object):
    instances = {}

    def __init__(self, path='sounds/peng.wav'):
        self.loop = False;
        #logging.debug("init sound object %s" % path)
        self.p = pyaudio.PyAudio()
        self.wf = wave.open(path, 'rb')
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True,
            start=False,
            stream_callback=self.playCallback)

        #logging.debug("channels: %d rate: %d" % (self.wf.getnchannels(), self.wf.getframerate()))
        Sound.instances[path] = self

    def playCallback(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        #logging.debug("PLAY CALLBACK " + str(len(data)) + " " + str(frame_count))

        if self.loop:
            if len(data) < 4096: # If file is over then rewind.
                self.wf.rewind()
                data += self.wf.readframes(frame_count - len(data)//4)

        return (data, pyaudio.paContinue)

    @classmethod
    def getInstance(cls, path):
        path = cls.getPath(path)
        if path not in cls.instances:
            cls.instances[path] = Sound(path)
        return cls.instances[path]

    @classmethod
    def closeAll(cls):
        for i in cls.instances.values():
            i.closeI()

    @classmethod
    def getPath(cls, path):
        basePath = os.path.join(os.path.dirname(__file__), 'sound')
        return os.path.join(basePath, path)

    @classmethod
    def play(cls, path):
        if bool(config.getValue('game.sound')) is False or path is None:
            return
        Sound.getInstance(path).playI()

    @classmethod
    def startLoop(cls, path):
        if bool(config.getValue('game.sound')) is False or path is None:
            return
        i = Sound.getInstance(cls.getPath(path))
        i.loop = True;
        i.playI()

    @classmethod
    def stopLoop(cls, path):
        if bool(config.getValue('game.sound')) is False or path is None:
            return
        i = Sound.getInstance(cls.getPath(path))
        i.loop = False;

    def playI(self):
        self.stopI()
        self.wf.rewind()
        self.stream.start_stream()

    def stopI(self):
        if not self.stream.is_stopped():
            #logging.debug("stopping stream")
            self.stream.stop_stream()
            #logging.debug("stream stopped")

    def closeI(self):
        self.stopI()
        self.stream.close()
        self.wf.close()
