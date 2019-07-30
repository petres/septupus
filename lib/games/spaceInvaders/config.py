from glob import glob
import os
import json

class ConfigManager(object):
    def __init__(self, path):
        path = os.path.join(path, 'config')
        files = glob(path + "/*.json")
        self.configs = {os.path.basename(f)[:-5]: json.load(open(f)) for f in files}


    def getElement(self, name, base):
        e = base
        for p in name.split('.'):
            e = e[p]
        return e

    # def setValue(self, name, value):
    #     self.getElement(name, self.configs).value = int(value)

    def getValue(self, name):
        return self.getElement(name, self.configs)


    def readConfig(self):

        # soundConfig = ConfigParser()
        # soundConfig.read('./etc/sound.cfg')

        # if soundConfig.getboolean('General', 'enabled'):
        #     Shoot.soundShooting     = soundConfig.get('Shoot', 'shooting')
        #     Game.background         = soundConfig.get('General', 'background')
        #     Shoot.soundCollision    = soundConfig.get('Shoot', 'invader')
        #
        #     Invader.cSpaceship     = soundConfig.get('Spaceship', 'invader')
        #     Goody.cSpaceship        = soundConfig.get('Spaceship', 'goody')
        #     Game.soundLost          = soundConfig.get('General', 'lost')
        #     Game.soundFull          = soundConfig.get('General', 'full')


        # robot = None
        # if gameConfig.robot['enabled']:
        #     robot = BotComm(robotConfig.get('Robot', 'serialPort'), g.robotMessage)
        #
        # Game.robot = robot
        pass

config = ConfigManager(os.path.dirname(__file__))
