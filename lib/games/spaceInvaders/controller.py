from .config import config
import curses

class Controller(object):
    def handleInput(self, game):
        self.input = self.screen.getch()
        self.checkControl(game)
        pos = self.getPosition(game.ship.coords[0])
        if type(pos) is float:
            pos = int(pos * (game.output.areas['game']['size'][0] - game.ship.size[0]))
        return (pos, self.getShoot())


class ScreenController(Controller):
    moveStepSize = 3

    def __init__(self, screen):
        self.input = None
        self.screen = screen

    def getPosition(self, oldPosition):
        m = 0
        if self.input == curses.KEY_LEFT:
            m = -1
        elif self.input == curses.KEY_RIGHT:
            m = 1

        x = oldPosition
        x += m * self.moveStepSize
        return x

    def getShoot(self):
        return self.input == ord(' ')

    def checkControl(self, game):
        if self.input == ord('q'):
            game.stopFlag = True
        elif self.input == ord('n'):
            game.generateGoodyType = "N"
        elif self.input == ord('o'):
            game.generateGoodyType = "O"
        elif self.input == ord('c'):
            game.generateGoodyType = None
        elif self.input == ord('p'):
            game.switchPause()
        elif self.input == ord('r'):
            game.play()
        elif self.input == ord('s'):
            game.end(game.EndState.quit)
