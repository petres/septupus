import logging
from enum import IntEnum, auto
from .spaceInvaders.controller import ScreenController
from .spaceInvaders.output import Output
from .spaceInvaders.game import Game
from .spaceInvaders.writer import ScreenWriter
from .spaceInvaders.config import config
from ..sharedManager import SharedManager
from numpy.random import choice


class CameraController(ScreenController):
    def __init__(self, screen, camera, manager):
        super().__init__(screen)
        self.camera = camera
        self.manager = manager

    def getShoot(self):
        #logging.debug(self.camera.getValue('output.position'))
        inputType = self.manager.getValue('game.inputType')
        if inputType == SpaceInvadersManager.InputTypes.camera and self.camera:
            return self.camera.getValue('output.shootFlag')
        elif inputType == SpaceInvadersManager.InputTypes.web:
            return self.manager.getValue('control.shootFlag')
        else:
            return super().getShoot()

    def getPosition(self, oldPosition):
        inputType = self.manager.getValue('game.inputType')
        if inputType == SpaceInvadersManager.InputTypes.camera and self.camera:
            return self.camera.getValue('output.position')
        elif inputType == SpaceInvadersManager.InputTypes.web:
            return self.manager.getValue('control.position')
        else:
            return super().getPosition(oldPosition)


class RobotCameraGame(Game):

    def __init__(self, screen, camera, robot, manager):
        controller = CameraController(screen=screen, camera=camera, manager=manager)
        output = Output(writers=[ScreenWriter(screen)])
        self.robot = robot
        self.manager = manager
        self.cupTaken = False
        super().__init__(output=output, controller=controller)

    def getStartStatus(self):
        status = super().getStartStatus()
        status['ml'] = 0
        return status

    def goodyCollected(self, type):
        self.status['goodies'].append(type)
        if self.robot:
            ml = self.robot.getValue('mixing.portion') * self.goodyTypes[type]['factor']
            self.status['ml'] += ml
            self.robot.pourIngredient(type, ml)
            if self.status['ml'] >= self.robot.getValue('mixing.volume') :
                self.end(self.EndState.won)

    def getNextGoodyType(self):
        g = None
        if self.robot:
            g = list(self.robot.getAvailableIngredients())
        return super().getNextGoodyType(g = g)

    def robotStateUpdate(self, state):
        if state == self.robot.State.readyCup:
            if self.state == self.State.stopped and self.cupTaken:
                self.play()
                self.cupTaken = False
            # if self.state == self.State.paused:
            #     self.state = self.State.running
            #     self.output.clearOverlay()

        if state == self.robot.State.ready:
            self.cupTaken = True

        return
        if state == self.robot.State.bottleEmpty:
            self.state = self.State.paused
            self.output.setOverlay("refillBottle")
        elif state == self.robot.State.readyCup:
            if self.state == self.State.stopped:
                self.play()
            if self.state == self.State.paused:
                self.state = self.State.running
                self.output.clearOverlay()
        elif state == self.robot.State.ready:
            if self.state == self.State.running:
                self.output.setOverlay("cupMissing")
            else:
                self.output.setOverlay("waiting")
            self.state = self.State.paused


class SpaceInvadersManager(SharedManager):
    file = "instance/spaceInvaders.json"

    class InputTypes(IntEnum):
        keyboard = auto()
        camera = auto()
        web = auto()

    def __init__(self, screen):
        self.screen = screen
        self.game = None
        super().__init__()

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
                'inputType': {
                    'name': "Use Camera Input", 'type': 'I',
                    'type': 'I', 'control': 'radio',
                    'value': self.InputTypes.keyboard.value,
                    'options': {i.name: i.value for i in self.InputTypes}
                },
                'shoot': {
                    'speed': {
                        'name': "Shoot Speed", 'type': 'I',
                        'control': 'range',
                        'min': 1, 'max': 40,
                        'value': config.getValue('game.shoot.speed')
                    },
                    'pause': {
                        'name': "Shoot Pause", 'type': 'I',
                        'control': 'range',
                        'min': 0, 'max': 40,
                        'value': config.getValue('game.shoot.pause')
                    }
                },
                'objectSpeed': {
                    'min': {
                        'name': "Min Object Speed", 'type': 'I',
                        'control': 'range',
                        'min': 1, 'max': 40,
                        'value': config.getValue('game.objectSpeed.min')
                    },
                    'max': {
                        'name': "Max Object Speed", 'type': 'I',
                        'control': 'range',
                        'min': 0, 'max': 40,
                        'value': config.getValue('game.objectSpeed.max')
                    }
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
                },
                'sound': {
                    'name': "Sound",
                    'type': 'b', 'control': 'radio',
                    'value': config.getValue('game.sound'),
                    'options': {i.name: i.value for i in self.OnOffFlags}
                },
            },
            'control': {
                'position': {
                    'name': "Position",
                    'type': 'f', 'control': 'range',
                    'min': 0, 'max': 1,
                    'value': 0.5
                },
                'shootFlag': {
                    'name': "Volume",
                    'type': 'b',
                    'value': 0
                },
            },
        }

    def run(self):
        self.game = RobotCameraGame(screen=self.screen, camera=self.modules['camera'],
                                    robot=self.modules['robot'], manager=self)

        # TODO INFORM AND REDO
        config.getValue = SpaceInvadersManager.getConfigValue
        SpaceInvadersManager.instance = self

        self.game.run()

    def robotStateUpdate(self, state):
        self.game.robotStateUpdate(state)

    def getDisplayVars(self):
        return {
            'control': [
                'game.sleepTime',
                'game.sound',
                'game.lifes',
                'game.inputType',
                'game.creationTimes.invaders',
                'game.creationTimes.goodies',
                'game.objectSpeed.min',
                'game.objectSpeed.max',
                'game.shoot.speed',
                'game.shoot.pause'
            ],
            'test': [
                'control.position',
            ]
        }

    # def setValue(self, name, value):
    #     self.getVar(name, self.shared).value = int(value)
    #     #config.configs['game']['sleep'] = int(value)

    def getConfigValue(name):
        if SpaceInvadersManager.instance.varExists(name):
            return SpaceInvadersManager.instance.getValue(name)
        return config.getElement(name, config.configs)
