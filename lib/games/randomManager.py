import logging
from enum import IntEnum, auto
from ..sharedManager import SharedManager
import time
from .shared.writer import ScreenWriter
from ..robot.robotManager import State

drinks = { 
    "vodkaOrange": {"vodka": 1/5, "orange": 4/5, },
    "ginOrange": {"gin": 1/5, "orange": 4/5, },
    "vodkaApple": {"vodka": 1/5, "apple": 4/5, },
    "vodkaMakava": {"vodka": 1/5, "makava": 4/5, },
}

class RandomManager(SharedManager):
    file = "instance/random.json"

    def __init__(self, screen):
        self.screen = screen
        self.writer = ScreenWriter(self.screen)
        super().__init__()
        
    def pourDrink(self, drink):
        logging.info(f'Pour Drink `{drink}`')
        self.robot.pourDrink(drinks[drink])

    def run(self):
        self.robot = self.modules['robot']
        
        while (True):
            robot_state = self.robot.state
            
            self.writer.addSigns((3, 3), f"RANDOM MANAGER")
            
            # self.writer.addSigns((3, 5), f"    Gesture: {gestureName}     ")
            self.writer.addSigns((3, 6), f"Robot State: {State(robot_state)}     ")
            # self.writer.addSigns((7, 5), gesture)
            
            
            if robot_state == State.readyCup:
                self.pourDrink("vodkaOrange")
            
            # self.screen.refresh()q
            
            keyPressed = self.screen.getch()
            
            if keyPressed == ord('q'):
                break
            
            time.sleep(0.1)
