import logging
import time
import os
from .object import Invader, Ship, Goody, Object, Shoot
from .utils import objectSigns
from .config import config
from .sound import Sound
from numpy.random import choice
from enum import IntEnum, auto

log = logging.getLogger("spaceInvaders")

#locale.setlocale(locale.LC_ALL, "")

class Game(object):
    class State(IntEnum):
        paused = auto()
        running = auto()
        countdown = auto()
        stopped = auto()

    class EndState(IntEnum):
        lost = auto()
        won = auto()
        quit = auto()

    class PauseState(IntEnum):
        manual = auto()

    countdownTime = 30
    stopFlag = False
    goodyTypes = {}
    generateGoodyType   = None

    # Config
    invaderCreationTime = None
    goodyCreationTime = None


    def __init__(self, output, controller=None):
        self.state = self.State.stopped
        self.time = 0
        self.output = output
        self.controller = controller
        self.ship = Ship(self)
        self.countdown = 0

        self.status = self.getStartStatus()

        for name, params in config.getValue('ingredients.beverages').items():
            categoryInfo = config.getValue('ingredients.catgories')[params['category']]
            self.goodyTypes[name] = {
                "name": name,
                "color": categoryInfo['color'],
                "design": os.path.join(config.getValue('design.ingredients.folder'), '%s.txt' % name),
                "display": params['display'] if 'display' in params.keys() else name.upper(),
                "factor": params['factor'] if 'factor' in params.keys() else categoryInfo['factor'],
                "category": params['category'],
            }

    def removeObjects(self):
        Object.objects = [self.ship]

    def getStartStatus(self):
        return {
            'goodies': [],
            'lifes': config.getValue('game.lifes')
        }

    def play(self):
        self.time = 0
        self.state = self.State.countdown

        Shoot.lastStartTime = 0
        self.removeObjects()
        self.output.clearOverlay()

        self.status = self.getStartStatus()
        self.countdown = 3

        Sound.startLoop(config.getValue('sound.background'))

    def loop(self):
        if self.controller:
            x, shoot = self.controller.handleInput(self)
        else:
            x, shoot = (self.ship.coords[0], False)

        if shoot:
            self.shoot()

        if x > self.output.areas['game']['size'][0] - self.ship.size[0]:
            x = self.output.areas['game']['size'][0] - self.ship.size[0]
        elif x < 0:
            x = 0

        self.ship.coords = (x, self.ship.coords[1])

        for o in list(Object.objects):
            o.check()

        self.output.printGame(self)

        # COUNTDOWN
        if self.state == self.State.countdown:
            self.output.setOverlay("countdown/%s" % self.countdown)
            if self.time > Game.countdownTime:
                self.countdown -= 1
                self.time = 0
                if self.countdown == 0:
                    self.state = self.State.running
                    self.output.clearOverlay()

        if self.state != self.State.paused:
            # CREATE OBJECT
            if self.state == self.State.running:
                if (self.time + 1) % (config.getValue('game.creationTimes.goodies') // 10) == 0:
                    Goody(self, type = self.goodyTypes[self.getNextGoodyType()])
                if self.time % (config.getValue('game.creationTimes.invaders') // 10) == 0:
                    Invader(self)
            self.time += 1

    def run(self):
        log.info('Starting main loop...')
        while not self.stopFlag:
            t0 = time.time()
            self.loop()
            time.sleep(max(0, t0 - time.time() + config.getValue('game.sleepTime')/1000))

        self.end(self.EndState.quit)
        self.cleanup()

    def shipCollision(self, o):
        if isinstance(o, Goody):
            # Goody Collected
            log.debug("goodyCollected: '%s'" % o.type)
            Sound.play(config.getValue('sound.collisions.ship.goody'))
            self.goodyCollected(o.type)
        elif isinstance(o, Invader):
            # Invader Collision
            if not self.ship.blinking:
                Sound.play(config.getValue('sound.collisions.ship.invader'))
                self.lifeLost()

    def goodyCollected(self, type):
        self.status['goodies'].append(type)
        if len(self.status['goodies']) >= config.getValue('game.goodies'):
             self.end(self.EndState.won)

    def objectShooted(self, o):
        if isinstance(o, Goody):
            sound = config.getValue('sound.collisions.shoot.goody')
        elif isinstance(o, Invader):
            sound = config.getValue('sound.collisions.shoot.invader')
        Sound.play(sound)

    def shoot(self):
        if Shoot.lastStartTime > self.time - config.getValue('game.shoot.pause'):
            return

        Sound.play(config.getValue('sound.shoot'))
        Shoot(self, coords = (self.ship.coords[0] + self.ship.size[0]//2, self.ship.coords[1] - 1))

    def getNextGoodyType(self, g = None, p = None):
        if g is None:
            g = list(self.goodyTypes.keys())

        if p is None:
            p = [1] * len(g)

        if self.generateGoodyType:
            for i, gn in enumerate(g):
                if self.goodyTypes[gn]['category'] != self.generateGoodyType:
                    p[i] = 0

        tp = sum(p)
        i = choice(range(len(p)), 1, p=[w/tp for w in p])[0]
        log.debug('select goody type %s' % g[i])
        return g[i]

    def switchPause(self):
        if self.state == self.State.paused:
            self.state = self.State.running
            Sound.startLoop(config.getValue('sound.background'))
        elif self.state == self.State.running:
            self.state = self.State.paused
            Sound.stopLoop(config.getValue('sound.background'))

    def end(self, status):
        log.info("end (status=%s)" % status.name)
        sound = None
        if status == self.EndState.lost:
            sound = config.getValue('sound.end.lost')
        elif status == self.EndState.won:
            sound = config.getValue('sound.end.won')
        if sound:
            Sound.play(sound)
        if status.name in config.getValue('design.endScreens'):
            self.output.setOverlay(config.getValue('design.endScreens')[status.name])
        self.removeObjects()
        self.state = self.State.stopped
        Sound.stopLoop(config.getValue('sound.background'))
        #log.debug("Ending now, threads alive: %s" % threading.active_count())

    def lifeLost(self):
        log.info("lifeLost")
        self.status['lifes'] -= 1
        if self.status['lifes'] == 0:
            self.end(self.EndState.lost)
        else:
            self.ship.blink()

    def cleanup(self):
        log.info("cleanup")
        Sound.closeAll()
