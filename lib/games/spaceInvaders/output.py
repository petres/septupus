import logging
import curses
import numpy as np

from .object import Goody, Object
from .utils import objectSigns

class Output(object):
    statusWidth = 28
    #statusWidth = 0

    def __init__(self, writers):
        self.writers = writers
        screenSize = writers[0].getSize()
        self.areas = {
            'full': {
                'coords': (0, 0),
                'size': screenSize
            },
            'game': {
                'coords': (1, 1),
                'size': (screenSize[0] - 2 - Output.statusWidth, screenSize[1] - 2)
            },
            'status': {
                'coords': (screenSize[0] - Output.statusWidth, 0),
                'size': (Output.statusWidth, screenSize[1])
            },
        }

        logging.debug("areas: %s" % self.areas)


        self.clearArea(area='full')

        self.printField()

    def printGame(self, game):
        self.clearArea('game')
        self.clearArea('status')

        self.printStatus(game)

        for o in list(Object.objects):
            self.printObject(o)

        # temp = '\n'
        # for y in range(self.matrix.shape[1]):
        #     for x in range(self.matrix.shape[0]):
        #         temp += chr(self.matrix[x, y, 0])
        #     temp += '\n'
        # f = open("screen.txt", "w")
        # f.write(temp)
        # f.close()


    def printField(self):
        fieldColor = 0
        fieldChar = "█"

        cx, cy = self.areas['game']['coords']
        sx, sy = self.areas['game']['size']

        for i in range(cx - 1, cx + sx + 1):
            self.addSigns((i, cy - 1), fieldChar, color = fieldColor)
            self.addSigns((i, cy + sy), fieldChar, color = fieldColor)

        for i in range(cy - 1, cy + sy + 1):
            self.addSigns((cx - 1, i), fieldChar, color = fieldColor)
            self.addSigns((cx + sx, i), fieldChar, color = fieldColor)

    def printStatus(self, game):
        ox, oy = (3, 1)
        self.addSigns((ox, oy), "Objects Count: %d" % len(Object.objects), area='status')
        os = {}
        for o in Object.objects:
            n = type(o).__name__
            if n in os.keys():
                os[n] += 1
            else:
                os[n] = 1

        for i, n in enumerate(os.keys()):
            self.addSigns((ox + 2, oy + 2 + i), "%s: %d" % (n, os[n]), area='status')


        oy = 12
        for i, line in enumerate(objectSigns.get("objects/heart.txt")):
            self.addSigns((ox - 1, oy + i), line, color = 2, area='status')

        for i, line in enumerate(objectSigns.get("objects/numbers/" + str(game.status['lifes']) + ".txt")):
            self.addSigns((ox, oy + 8 + i), line, area='status')

        for i, line in enumerate(objectSigns.get("objects/bottle.txt")):
            self.addSigns((ox + 12, oy + i), line, color = 4, area='status')

        for i, line in enumerate(objectSigns.get("objects/numbers/" + str(game.status['count']) + ".txt")):
            self.addSigns((ox + 12, oy + 8 + i), line, area='status')

        # self.addSigns((x,10), "count:  " + str(game.status['count']))
        # self.addSigns((x,11), "lifes:   " + str(game.status['lifes']))
        # self.addSigns((x,12), "time:    " + str(game.time))

        #
        # if game.cupThere:
        #     self.printGlass((x - 13, self.screenSize[1] - 24), game.status["goodies"])
        #     self.printMl((x - 15, self.screenSize[1] - 31), game.status["ml"])
        #
        # if self.screenSize[1] - 31 - (y + 15) > 10:
        #     for i, line in enumerate(objectSigns.get("objects/lebertron.txt")):
        #         self.addSigns((self.statusPos[0] + 1,  (y + 16) + (self.screenSize[1] - 31 - (y + 15) - 9)//2 + i), line, color = 7)


    def printCountdown(self, nr):
        self.centeredOutput("screens/countdown/" + str(nr) + ".txt")

    def printMl(self, pos, ml):
        x, y = pos
        color = 3

        if ml > 100:
            for i, line in enumerate(objectSigns.get("objects/lifes/" + str(int(ml/100)) + ".txt")):
                self.addSigns((x, y + i), line, color = color)

        x += 8
        if ml > 10:
            for i, line in enumerate(objectSigns.get("objects/lifes/" + str((ml/10)%10) + ".txt")):
                self.addSigns((x, y + i), line, color = color)

        x += 8
        for i, line in enumerate(objectSigns.get("objects/lifes/" + str(ml%10) + ".txt")):
            self.addSigns((x, y + i), line, color = color)


    def centeredOutput(self, file, area='game'):
        signs = objectSigns.get(file)
        w, h = (len(signs[0]), len(signs))
        x, y = self.areas[area]['size']
        bx = (x - w) // 2
        by = (y - h) // 2
        for i, line in enumerate(signs):
            ty = by + i
            self.addSigns((bx, ty), line, area=area)


    def printGlass(self, pos, goodies):
        x, y = pos
        top = objectSigns.get("objects/glass/top.txt")
        bottom = objectSigns.get("objects/glass/bottom.txt")

        body = []
        h = max(11, len(goodies))
        for i in range(h, -1, -1):
            if i > len(goodies) or len(goodies) == 0:
                body.append("||             ||")
            elif i == len(goodies):
                body.append("|:--.._____..--:|")
            elif i < len(goodies):
                body.append("||" + Goody.types[goodies[i]]["name"].center(13, " ") + "||")

        glass = top[:-1] + body + bottom
        for l in glass:
            y += 1
            self.addSigns((x, y), l)

    def printObject(self, o):
        x, y = o.getMapCoords()

        w, h = o.size

        if y > self.areas['game']['size'][1] + h or y < 0:
            Object.objects.remove(o)
            return

        signs = o.getSigns()

        for i, line in enumerate(o.signs):
            py = y + i
            if py < self.areas['game']['size'][1] and py >= 0:
                for j, sign in enumerate(line):
                    if sign != " ":
                        px = x + j
                        self.addSigns((px, py), sign, area = 'game', color = o.color)
        #self.addSigns((x, y), 'X', area = 'game', color = 2)

    def transCoords(self, coords, area):
        cx, cy = coords
        acx, acy = self.areas[area]['coords']
        return (cx + acx, cy + acy)

    def addSigns(self, coords, signs, area='full', color=0):
        coords = self.transCoords(coords, area)
        for writer in self.writers:
            writer.addSigns(coords, signs, color)

    def clearArea(self, area='full'):
        a = self.areas[area]
        for writer in self.writers:
            writer.clearArea(a['coords'], a['size'])
