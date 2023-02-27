#!/usr/bin/env python
from web import WebManager
from lib.multiManager import MultiManager
from lib.camera.cameraManager import CameraManager
from lib.robot.robotManager import RobotManager
from lib.robot.serialManager import SerialManager
from lib.games.spaceInvadersManager import SpaceInvadersManager
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

    modules = {
        'serial': SerialManager(),
        'camera': CameraManager(),
        'web': WebManager(),
        'robot': RobotManager(),
        # 'spaceInvaders': SpaceInvadersManager(screen),
        'nodding': NoddingManager(screen),
    }

    for n, m in modules.items():
        m.setModules(modules)
        m.initSharedVars()
        m.load()

    #modules['serial'].start()
    modules['camera'].start()
    modules['web'].start()

    time.sleep(0.01)

    modules['nodding'].run()

    for n, m in modules.items():
        m.save()
        if isinstance(m, MultiManager) and m.isRunning():
            m.stop()

#main()
curses.wrapper(main)
