from .utils import objectSigns
import random
import logging
from numpy.random import choice
from .config import config
import os

class Object(object):
    objects = []
    posArrays = {}
    defaultSpeed = 2

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
                Object.defaultSpeed, Object.defaultSpeed * 2)
        else:
            self.speed = speed

        Object.objects.append(self)

        if len(signsArray) > 0:
            self.currentSigns = 0
            self.signs = signsArray[0]

        self.size = (max([len(l) for l in signs]), len(signs))


    def setRandomXPos(self, output, y=None):
        if y is None:
            y = 0
        # x = random.randint(
        #     2 + self.info['rWidth'], output.areas['game']['size'][0] - 2 - self.info['rWidth'])
        x = random.randint(0, output.areas['game']['size'][0] - self.size[0])
        self.coords = (x, y)

    def getSigns(self):
        if len(self.signsArray) > 0:
            if self.game.time % self.switchSignsTime == 0:
                self.currentSigns = (self.currentSigns + 1) % len(self.signsArray)
                self.signs = self.signsArray[self.currentSigns]
        return self.signs

    # TODO IMPROVE
    def getPosArray(self):
        # x, y = self.getMapCoords()
        # return [(x + j, y + i) for i, line in enumerate(self.signs) for j, sign in enumerate(line) if sign != ' ']
        signsT = tuple(self.signs)
        if signsT not in Object.posArrays.keys():
            Object.posArrays[signsT] = [(j, i) for i, line in enumerate(self.signs) for j, sign in enumerate(line) if sign != ' ']
        x, y = self.getMapCoords()
        return [(x + i, y + j) for i, j in Object.posArrays[signsT]]

    def check(self):
        if len(set(self.getPosArray()).intersection(self.game.ship.getPosArray())) > 0:
            try:
                Object.objects.remove(self)
            except ValueError as e:
                pass
            self.collision()

    def collision(self):
        pass

    def getMapCoords(self):
        return (self.coords[0], self.coords[1] + (self.game.time - self.startTime) // self.speed)


class Shoot(Object):
    soundShooting   = None
    soundCollision  = None
    lastStartTime   = 0
    diffBetween     = 15
    def __init__(self, game, **args):
        logging.debug("init Shoot")
        if Shoot.lastStartTime > game.time - Shoot.diffBetween:
            return

        Shoot.lastStartTime = game.time

        args["signs"] = objectSigns.get("objects/shoot.txt")
        args["color"] = 2
        args["speed"] = -1
        if Shoot.soundShooting is not None:
            Sound.play(Shoot.soundShooting)
        super(Shoot, self).__init__(game, **args)

    def check(self):
        for o in Object.objects:
            if isinstance(o, Invader) or isinstance(o, Goody):
                if len(set(self.getPosArray()).intersection(o.getPosArray())) > 0:
                    Object.objects.remove(o)
                    Object.objects.remove(self)
                    if Shoot.soundCollision is not None:
                        Sound.play(Shoot.soundCollision)
                    break


class Invader(Object):
    invaders = objectSigns.list(config.getValue('design.invaders.folder'))
    color = config.getValue('design.invaders.color')
    cSpaceship  = None

    def collision(self):
        if not self.game.ship.blinking:
            if Invader.cSpaceship is not None:
                Sound.play(Invader.cSpaceship)
            self.game.lifeLost()


    def __init__(self, game, **args):
        if "signs" not in args:
            i = random.randint(0, len(Invader.invaders) - 1)
            args["signs"] = objectSigns.get(Invader.invaders[i])
            args["color"] = Invader.color
        super(Invader, self).__init__(game, **args)



class Goody(Object):
    portion = config.getValue('robot.mixing.portion')
    volume = config.getValue('robot.mixing.volume')

    types = []
    for name, params in config.getValue('robot.ingredients').items():
        types.append({
                "color":    config.getValue('design.ingredients.categories')[params['category']]['color'],
                "design":   os.path.join(config.getValue('design.ingredients.folder'), name + '.txt'),
                "name":     name.upper(),
                "arduino":  params['arduino'],
                "factor":   params['factor'] if 'factor' in params.keys() else config.getValue('robot.ingredientsCatgories')[params['category']]['factor'],
                "category": params['category']
        })

    cSpaceship  = None
    generateT   = None

    def collision(self):
        if Goody.cSpaceship is not None:
            Sound.play(Goody.cSpaceship)
        self.game.status['ml']    += Goody.portion * Goody.types[self.type]["factor"]
        for i in range(Goody.types[self.type]["factor"]):
            self.game.status['goodies'].append(self.type)
        self.game.status['count'] += 1

        if self.game.robot is not None:
            self.game.robot.pourBottle(Goody.types[self.type]["arduino"], Goody.portion * Goody.types[self.type]["factor"])
        if self.game.status['ml'] >= Goody.volume:
            self.game.full()

    def __init__(self, game, **args):
        self.type = self.getNextGoodyType(game.status["goodies"])

        try:
            args["signs"] = objectSigns.get(Goody.types[self.type]["design"])
            args["color"] = Goody.types[self.type]["color"]
        except Exception:
            args["signs"] = objectSigns.get("objects/ingredients/default.txt")
            args["color"] = 2

        super(Goody, self).__init__(game, **args)

    def getNextGoodyType(self, collectedGoodies):
        weights = [1] * len(Goody.types)

        if Goody.generateT:
            for i, wGoody in enumerate(Goody.types):
                if wGoody['category'] != Goody.generateT:
                    weights[i] = 0
        tw = sum(weights)
        return choice(range(len(weights)), 1, p=[w/tw for w in weights])[0]


class Ship(Object):
    designArray = objectSigns.list(config.getValue('design.ship.folder'))
    color = config.getValue('design.ship.color')
    blinkColor = 2

    def __init__(self, game, **args):
        args["signs"] = objectSigns.get(Ship.designArray[0])
        signsArray = []
        for design in Ship.designArray:
            signsArray.append(objectSigns.get(design))
        args["signsArray"] = signsArray
        args["color"] = Ship.color
        args["switchSignsTime"] = 10
        self.switchBlinkTime = 8
        self.switchBlinkDuration = 50
        self.blinking = False
        super(Ship, self).__init__(game, **args)

    def getMapCoords(self):
        return (self.coords[0], self.coords[1])

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
