#!/usr/bin/env python
# from web import WebManager
# from lib.multiManager import MultiManager
# from lib.camera.cameraManager import CameraManager
# from lib.robot.robotManager import RobotManager
# from lib.robot.serialManager import SerialManager
# from lib.games.spaceInvadersManager import SpaceInvadersManager
from lib.games.noddingManager import NoddingManager
import logging
import sys
import time
import curses

# setup log file to subdir
logging.basicConfig(filename='log/debug.log', level=logging.DEBUG,
                    format='%(levelname)8s - %(name)s %(relativeCreated)d: %(message)s')

sys.stderr = open('log/error.log', 'w')

def main(screen = None):
    m = NoddingManager(screen)

    # screen.clear()

    screen.addstr(2, 2, 'adf')

    m.run()


#main()
curses.wrapper(main)
