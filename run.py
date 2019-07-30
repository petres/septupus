#!./venv/bin/python3
from web import WebManager
from flask import request
import threading
from lib.multiManager import MultiManager
from lib.camera.cameraManager import CameraManager
from lib.robot.robotManager import RobotManager
from lib.robot.serialManager import SerialManager
from lib.games.spaceInvadersManager import SpaceInvadersManager
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
        'spaceInvaders': SpaceInvadersManager(screen)
    }

    for n, m in modules.items():
        m.setModules(modules)
        m.initSharedVars()
        m.load()

    #modules['serial'].start()
    modules['camera'].start()
    modules['web'].start()

    time.sleep(0.01)

    modules['spaceInvaders'].run()

    for n, m in modules.items():
        m.save()
        if isinstance(m, MultiManager) and m.isRunning():
            m.stop()

#main()
curses.wrapper(main)
