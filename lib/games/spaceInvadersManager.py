import logging
from .spaceInvaders.controller import Controller
from .spaceInvaders.output import Output
from .spaceInvaders.game import ScreenGame
from .spaceInvaders.writer import ScreenWriter
from .spaceInvaders.config import config
from ..sharedManager import SharedManager


class SpaceInvadersManager(SharedManager):
    def __init__(self, screen):
        controller = Controller(screen=screen)
        gameOutput = Output(writers=[ScreenWriter(screen)])
        self.game = ScreenGame(output=gameOutput, controller=controller)
        super().__init__()
        self.initVars()
        config.getValue = SpaceInvadersManager.getConfigValue
        SpaceInvadersManager.instance = self

    def getVars(self):
        return {
            'game': {
                'sleepTime': {
                    'name': "Sleep (ms)",
                    'type': 'I', 'control': 'range',
                    'min': 5, 'max': 50,
                    'value': config.getValue('game.sleepTime')
                },
                'lifes': {
                    'name': "Lifes", 'type': 'I',
                    'control': 'range',
                    'min': 1, 'max': 9,
                    'value': config.getValue('game.lifes')
                },
                'creationTimes': {
                    'invaders': {
                        'name': "Creation Time, Invaders",
                        'type': 'I', 'control': 'range',
                        'min': 200, 'max': 5000,
                        'value': config.getValue('game.creationTimes.invaders')
                    },
                    'goodies': {
                        'name': "Creation Time, Goodies",
                        'type': 'I', 'control': 'range',
                        'min': 200, 'max': 5000,
                        'value': config.getValue('game.creationTimes.goodies')
                    }
                }, 'useCamera': {
                    'name': "Camera Input",
                    'type': 'I', 'control': 'radio',
                    'value': 0,
                    'options': {i.name: i.value for i in self.OnOffFlags}
                }
            },
            'robot': {
                'mixing': {
                    'portion': {
                        'name': "Portion",
                        'type': 'I', 'control': 'range',
                        'min': 10, 'max': 50,
                        'value': config.getValue('robot.mixing.portion')
                    },
                    'volume': {
                        'name': "Volume",
                        'type': 'I', 'control': 'range',
                        'min': 100, 'max': 500,
                        'value': config.getValue('robot.mixing.volume')
                    }
                }
            }
        }

    def run(self):
        self.game.run()

    def getDisplayVars(self):
        return {
            'control': [
                'game.sleepTime',
                'game.lifes',
                'game.creationTimes.invaders',
                'game.creationTimes.goodies',
                'game.useCamera',
            ],
            'mixing': [
                'robot.mixing.portion',
                'robot.mixing.volume',
            ]
        }

    # def setValue(self, name, value):
    #     self.getVar(name, self.shared).value = int(value)
    #     #config.configs['game']['sleep'] = int(value)

    def getConfigValue(name):
        if SpaceInvadersManager.instance.varExists(name):
            return SpaceInvadersManager.instance.getValue(name)
        return config.getElement(name, config.configs)
