#!/usr/bin/env python
from web import WebManager
from lib.multiManager import MultiManager
from lib.robot.robotManager import RobotManager
from lib.robot.serialManager import SerialManager
from lib.games.randomManager import RandomManager
import logging
import sys
import curses

# setup log file to subdir
logging.basicConfig(filename='log/debug.log', level=logging.DEBUG,
                    format='%(levelname)8s - %(name)s %(relativeCreated)d: %(message)s')

sys.stderr = open('log/error.log', 'w')

def main(screen = None):

    modules = {
        'serial': SerialManager(),
        'web': WebManager(),
        'robot': RobotManager(),
        'game': RandomManager(screen),
    }

    for n, m in modules.items():
        m.setModules(modules)
        m.initSharedVars()
        m.load()

    modules['serial'].start()
    modules['web'].start()

    modules['game'].run()

    for n, m in modules.items():
        m.save()
        if isinstance(m, MultiManager) and m.isRunning():
            m.stop()

#main()
curses.wrapper(main)
