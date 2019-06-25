import curses

class Controller(object):
    LEFT    = -1
    RIGHT   =  1
    QUIT    = -10
    RETRY   = -11
    SHOOT   = -12
    PAUSE   = -13
    CUPTEST = -15

    def __init__(self, screen = None, position = False, mirror = False, margin = 0):
        self.imp = None
        self.screen = screen
        self.position = position
        self.mirror = mirror
        self.margin = margin

    def setImp(self, imp):
        self.imp = imp

    def getInput(self):
        c, k = self.getKeyboardInput();

        if k is not None:
            return k

        if self.imp is not None:
            return self.imp.getInput(c)

    def getPosition(self):
        pos = self.imp.getPosition()

        if self.margin > 0:
            pos = pos*(1 + 0.01*2*self.margin) - 0.01*self.margin

        if pos > 1:
            pos = 1
        elif pos < 0:
            pos = 0

        if self.mirror:
            return 1 - pos
        else:
            return pos

    def getKeyboardInput(self):
        if self.screen is None:
            return None

        c = self.screen.getch()

        if c == curses.KEY_LEFT:
            return (c, Controller.LEFT)
        elif c == curses.KEY_RIGHT:
            return (c, Controller.RIGHT)
        elif c == ord('q'):
            return (c, Controller.QUIT)
        elif c == ord('r'):
            return (c, Controller.RETRY)
        elif c == ord(' '):
            return (c, Controller.SHOOT)
        elif c == ord('p'):
            return (c, Controller.PAUSE)
        elif c == ord('n'):
            Goody.generateT = "N"
        elif c == ord('o'):
            Goody.generateT = "O"
        elif c == ord('c'):
            Goody.generateT = None
        elif c == ord('l'):
            return (c, Controller.CUPTEST)

        return (c, None)

    def close(self):
        if self.imp is not None:
            self.imp.close()
