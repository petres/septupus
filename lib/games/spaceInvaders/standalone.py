import logging
import curses
from .output import Output
from .writer import ScreenWriter
from .game import ScreenGame
from .controller import Controller

logging.basicConfig(filename='debug.log', level=logging.DEBUG,
                    format='%(levelname)8s - %(asctime)s: %(message)s')

def main(screen = None):
    controller = Controller(screen=screen)
    output = Output(writers=[ScreenWriter(screen)])
    game = ScreenGame(output=output, controller=controller)

    try:
        game.run()
    except Exception as e:
        raise e
    finally:
        game.cleanup()
#main()
curses.wrapper(main)
