import logging
import time
import os
from .object import Invader, Ship, Goody, Object, Shoot
from .controller import Controller
from .utils import objectSigns
from .config import config

#locale.setlocale(locale.LC_ALL, "")

class Game(object):
    moveStepSize = 3
    createObjects = False
    countdownTime = 30
    stopFlag = False

    # Config
    invaderCreationTime = None
    goodyCreationTime = None

    background = None
    soundLost = None
    soundFull = None


    def __init__(self, output, robot=None):
        self.time       = 0
        self.output     = output
        self.robot      = robot
        self.pause      = False
        self.ship       = Ship(self)
        self.ship.coords = ((self.output.areas['game']['size'][0] - self.ship.size[0]) // 2, self.output.areas['game']['size'][1] - self.ship.size[1])
        self.countdown  = 0

        self.status     = {}
        self.setStartStatus()
        self.overlay    = None
        self.oTime      = None
        self.cupThere   = False
        self.cupTaken   = True

        self.gameStarted = False

    def removeObjects(self):
        logging.debug("removing objects")
        Object.objects = [self.ship]

    def setStartStatus(self):
        self.status['goodies'] = []
        self.status['lifes']   = config.getValue('game.lifes')
        self.status['ml']      = 0
        self.status['count']   = 0

    def prepare(self):
        self.time = 0
        self.removeObjects()
        self.createObjects = False
        self.setStartStatus()
        #self.output.prepareGame()
        self.countdown = 3
        self.overlay = None
        self.gameStarted = True
        self.cupTaken   = False
        Shoot.lastStartTime = 0
        if Game.background is not None:
            Sound.startLoop(Game.background)

    def loop(self):
        x = self.handleInput()

        if x > self.output.areas['game']['size'][0] - self.ship.size[0]:
            x = self.output.areas['game']['size'][0] - self.ship.size[0]
        elif x < 0:
            x = 0

        self.ship.coords = (x, self.ship.coords[1])

        for o in list(Object.objects):
            o.check()

        self.output.printGame(self)

        # COUNTDOWN
        if self.countdown > 0:
            self.output.printCountdown(self.countdown)
            if self.time > Game.countdownTime:
                self.countdown -= 1
                self.time = 0
                if self.countdown == 0:
                    self.createObjects = True

        if self.overlay is not None:
            self.output.centeredOutput('screens/%s.txt' % self.overlay)

        if not self.pause:
            # CREATE OBJECT
            if self.createObjects:
                if (self.time + 1) % (config.getValue('game.creationTimes.goodies') // 10) == 0:
                    g = Goody(self)
                    g.setRandomXPos(self.output)
                if self.time % (config.getValue('game.creationTimes.invaders') // 10) == 0:
                    o = Invader(self)
                    o.setRandomXPos(self.output)
            self.time += 1

    def run(self):
        logging.info('Starting main loop...')
        while not self.stopFlag:
            t0 = time.time()
            self.loop()
            time.sleep(max(0, t0 - time.time() + config.getValue('game.sleepTime')/1000))

        self.end("quit")

    def handleInput(self):
        return self.ship.coords[0]

    def switchPause(self):
        self.pause = not self.pause

    def full(self):
        self.end("overFull")

    def end(self, status):
        if status == "overLifes" and Game.soundLost is not None:
            Sound.play(Game.soundLost)
        if status == "overFull" and Game.soundFull is not None:
            Sound.play(Game.soundFull)

        logging.info("Ending game now (status=%s)" % status)
        #logging.debug("threads alive: %s" % threading.active_count())
        self.overlay = status
        self.removeObjects()
        self.cupTaken = False
        logging.debug("clearing screen")
        #screen.clear()
        #self.output.printField()
        self.gameStarted = False
        self.createObjects = False
        if Game.background is not None:
            logging.debug("Game.background.stopLoop()")
            if Game.background is not None:
                Sound.stopLoop(Game.background)
            logging.debug("background sound stopped successfully")
        #logging.debug("Ending now, threads alive: %s" % threading.active_count())

    def lifeLost(self):
        logging.info("you lost a life!")
        self.status['lifes'] = self.status['lifes'] - 1
        logging.debug("status=%s" % self.status)
        if self.status['lifes'] == 0:
            self.end("overLifes")
        else:
            self.ship.blink()

    def robotMessage(self, message):
        if message == "bottleEmpty":
            self.pause = True
            self.overlay = "refillBottle"
        elif message == "bottleEmptyResume":
            self.pause = False
            self.overlay = None
        elif message == "cupThere":
            self.cupThere = True
            if self.gameStarted:
                self.overlay = None
                self.pause = False
        elif message == "cupNotThere":
            self.cupThere = False
            self.cupTaken = True
            if self.countdown > 0:
                self.gameStarted = False
                self.countdown = 0
            if self.gameStarted:
                self.pause = True
                self.overlay = "cupMissing"
            if not self.gameStarted:
                self.overlay = "waiting"

    def cleanup(self):
        #if soundConfig.enabled:
        #    Sound.closeAll()

        if self.robot is not None:
            self.robot.close()

class ScreenGame(Game):
    def __init__(self, output, controller, robot=None):
        self.controller = controller
        super().__init__(output = output, robot = robot)

    def handleInput(self):
        d = self.controller.getInput()

        if d == Controller.QUIT:
            self.stopFlag = True
        elif d == Controller.SHOOT:
            #o = Shoot(self, coords = (self.ship.coords[0], self.ship.coords[1] - self.ship.info['rHeight'] - 1))
            o = Shoot(self, coords = (self.ship.coords[0] + self.ship.size[0]//2, self.ship.coords[1] - 1))
        elif d == Controller.CUPTEST:
            if self.cupThere:
                self.robotMessage("cupNotThere")
            else:
                self.robotMessage("cupThere")

        # start game
        if d == Controller.RETRY or (not self.gameStarted and self.cupThere and self.cupTaken):
            self.prepare()

        if d == Controller.PAUSE:
            self.switchPause()

        x = self.ship.coords[0]

        if self.controller.position == False:
            m = 0
            if d == Controller.LEFT:
                m = -1
            elif d == Controller.RIGHT:
                m = 1

            x = self.ship.coords[0]
            x += m * self.moveStepSize
        else:
            x = int(self.controller.getPosition() * self.output.areas['game']['size'][0])

        return x
