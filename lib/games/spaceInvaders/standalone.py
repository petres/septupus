import logging
import curses
from .output import Output
from .writer import ScreenWriter
from .game import Game
from .controller import ScreenController

logging.basicConfig(filename='debug.log', level=logging.DEBUG,
                    format='%(levelname)8s - %(asctime)s: %(message)s')

def main(screen = None):
    controller = ScreenController(screen=screen)
    output = Output(writers=[ScreenWriter(screen)])
    game = Game(output=output, controller=controller)

    try:
        game.run()
    except Exception as e:
        raise e
    finally:
        game.cleanup()
#main()
curses.wrapper(main)
