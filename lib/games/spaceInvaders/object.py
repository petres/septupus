from .utils import objectSigns
import random
from .config import config


class Object(object):
    objects = []
    posArrays = {}
    defaultSpeed = 4

    def __init__(self, game, coords=None, signs=None, speed=None, color=None,
                 signsArray=[], switchSignsTime=None):
        self.game            = game
        self.coords          = coords
        self.signs           = signs
        self.color           = color
        self.startTime       = game.time
        self.signsArray      = signsArray
        self.switchSignsTime = switchSignsTime

        if speed is None:
            self.speed = random.randint(
                config.getValue('game.objectSpeed.min'),
                config.getValue('game.objectSpeed.max'))
        else:
            self.speed = speed

        Object.objects.append(self)

        if len(signsArray) > 0:
            self.currentSigns = 0
            self.signs = signsArray[0]

        self.size = (max([len(l) for l in signs]), len(signs))

    def setRandomXPos(self, y=0):
        x = random.randint(0, self.game.output.areas['game']['size'][0] - self.size[0])
        self.coords = (x, y)

    def getSigns(self):
        if len(self.signsArray) > 0:
            if self.game.time % self.switchSignsTime == 0:
                self.currentSigns = (self.currentSigns + 1) % len(self.signsArray)
                self.signs = self.signsArray[self.currentSigns]
        return self.signs

    def getPosArray(self):
        signsT = tuple(self.signs)
        if signsT not in Object.posArrays.keys():
            Object.posArrays[signsT] = [(j, i) for i, line in enumerate(self.signs) for j, sign in enumerate(line) if sign != ' ']
        x, y = self.getCoords()
        return [(x + i, y + j) for i, j in Object.posArrays[signsT]]

    def check(self):
        if len(set(self.getPosArray()).intersection(self.game.ship.getPosArray())) > 0:
            try:
                Object.objects.remove(self)
            except ValueError as e:
                pass
            self.game.shipCollision(self)

    def getCoords(self):
        if self.speed != 0:
            return (self.coords[0], self.coords[1] + (self.game.time - self.startTime) * self.speed // 20)
        else:
            return self.coords


class Shoot(Object):
    lastStartTime   = 0

    def __init__(self, game, **args):
        args["signs"] = objectSigns.get("objects/shoot.txt")
        args["color"] = 2
        args["speed"] = -1*config.getValue('game.shoot.speed')
        # TODO: MAKE IT DEPENDENT OF DESIGN
        args["coords"] = (args["coords"][0] - 1, args["coords"][1])
        super(Shoot, self).__init__(game, **args)
        Shoot.lastStartTime = game.time

    def check(self):
        for o in Object.objects:
            if isinstance(o, Invader) or isinstance(o, Goody):
                if len(set(self.getPosArray()).intersection(o.getPosArray())) > 0:
                    Object.objects.remove(o)
                    Object.objects.remove(self)
                    self.game.objectShooted(o)
                    break


class Invader(Object):
    invaders = objectSigns.list(config.getValue('design.invaders.folder'))
    color = config.getValue('design.invaders.color')

    def __init__(self, game, **args):
        if "signs" not in args:
            i = random.randint(0, len(Invader.invaders) - 1)
            args["signs"] = objectSigns.get(Invader.invaders[i])
            args["color"] = Invader.color
        super(Invader, self).__init__(game, **args)
        self.setRandomXPos()


class Goody(Object):
    def __init__(self, game, type, **args):
        self.type = type['name']
        try:
            args["signs"] = objectSigns.get(type["design"])
            args["color"] = type["color"]
        except Exception:
            args["signs"] = objectSigns.get("objects/ingredients/default.txt")
            args["color"] = 2
        super(Goody, self).__init__(game, **args)
        self.setRandomXPos()


class Ship(Object):
    designArray = objectSigns.list(config.getValue('design.ship.folder'))
    color = config.getValue('design.ship.color')
    blinkColor = 2
    switchBlinkTime = 3
    switchBlinkDuration = 24

    def __init__(self, game, **args):
        args["signs"] = objectSigns.get(Ship.designArray[0])
        signsArray = []
        for design in Ship.designArray:
            signsArray.append(objectSigns.get(design))
        args["signsArray"] = signsArray
        args["color"] = Ship.color
        args["switchSignsTime"] = 4
        args["speed"] = 0
        self.blinking = False
        super(Ship, self).__init__(game, **args)
        self.coords = ((game.output.areas['game']['size'][0] - self.size[0]) // 2,
                       game.output.areas['game']['size'][1] - self.size[1])

    def check(self):
        if self.blinking:
            if self.blinkTime % self.switchBlinkTime == 0:
                if self.blinkTime > self.switchBlinkDuration:
                    self.color, self.blinkColor = self.orgColor, self.orgBlinkColor
                    self.blinking = False
                else:
                    self.color, self.blinkColor  = self.blinkColor, self.color
            self.blinkTime += 1

    def blink(self):
        self.orgColor, self.orgBlinkColor = self.color, self.blinkColor
        self.blinkTime = 0
        self.blinking = True
