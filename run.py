#!./venv/bin/python
from web import start_app
from flask import request
import threading
from lib.camera.cameraManager import CameraManager
from lib.games.spaceInvadersManager import SpaceInvadersManager
import logging
import sys
import time
import curses

# setup log file to subdir
logging.basicConfig(filename='log/debug.log', level=logging.DEBUG,
                    format='%(levelname)8s - %(asctime)s: %(message)s')

sys.stderr = open('log/error.log', 'w')

def main(screen = None):
    # Camera
    camera = CameraManager()
    camera.startProcess()

    # Game: Space Invaders
    spaceInvaders = SpaceInvadersManager(screen)

    modules = {
        'spaceInvaders': spaceInvaders,
        'robot': None,
        'camera': camera
    }

    # Web
    web = threading.Thread(target=start_app, args=(modules, ))
    web.setDaemon(True)
    web.start()

    time.sleep(0.1)
    spaceInvaders.run()

    camera.save()

    camera.stopProcess()


#main()
curses.wrapper(main)
