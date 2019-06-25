import os
from glob import glob

class ObjectSigns(object):
    path = None
    def __init__(self, path):
        self.loadedObjects = {}
        ObjectSigns.path = os.path.join(path, 'design')

    def get(self, fileName):
        if fileName in self.loadedObjects.keys():
            return self.loadedObjects[fileName]

        signs = self.load(fileName)
        self.loadedObjects[fileName] = signs
        return signs

    @classmethod
    def load(cls, fileName):
        with open(os.path.join(cls.path, fileName), 'r') as f:
            return f.read().split("\n")[:-1]

    @classmethod
    def list(cls, folder):
        return [os.path.join(folder, os.path.basename(f)) for f in glob(os.path.join(cls.path, folder) + "/*.txt")]

objectSigns = ObjectSigns(os.path.dirname(__file__))
