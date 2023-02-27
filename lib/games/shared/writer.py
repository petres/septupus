import logging
import curses
import numpy as np

class Writer(object):
    def __init__(self, screenSize):
        self.screenSize = screenSize

    def addSigns(self, coords, signs, color=0):
        pass

    def clearArea(self, coords, size):
        cx, cy = coords
        sx, sy = size
        for i in range(cy, cy + sy):
            self.addSigns((cx, i), ' ' * sx)

    def getSize(self):
        return self.screenSize

class ScreenWriter(Writer):
    def __init__(self, screen):
        self.screen = screen
        self.screen.nodelay(1)

        curses.curs_set(0)
        curses.start_color()

        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

        logging.info("Possible number of different colors: %s" % curses.COLORS)

        super().__init__(self.screen.getmaxyx()[::-1])


    def addSigns(self, coords, signs, color=0):
        cx, cy = coords
        try:
            self.screen.addstr(cy, cx, signs, curses.color_pair(color))
            # logging.info("addSigns")
        except curses.error:
            pass

class MatrixWriter(Writer):
    def __init__(self, screenSize):
        #t = np.dtype([('char', 'B'), ('color', 'B')])
        #self.matrix = np.empty((x, y), dtype=t)
        self.matrix = np.empty((screenSize[0], screenSize[1], 2), dtype='int')
        super().__init__(screenSize)

    def addSigns(self, coords, signs, color=0):
        #self.matrix[coords[0]:(coords[0]+len(sign)), coords[1]] = [(ord(s), color) for s in sign]
        self.matrix[cx:(cx + len(signs)), cy, 0] = [ord(s) for s in signs]
        self.matrix[cx:(cx + len(signs)), cy, 1] = color

    def clearArea(self, coords, size):
        cx, cy = a['coords']
        sx, sy = a['size']

        #self.matrix[coords[0]:(coords[0] + size[0]), coords[1]:(coords[1] + size[1])] = (ord(sign), 0)
        self.matrix[cx:(cx + sx), cy:(cy + sy), 0] = ord(' ')
        self.matrix[cx:(cx + sx), cy:(cy + sy), 1] = 0
        self.clearAreaImp(a['coords'], a['size'])
