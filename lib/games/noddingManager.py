import logging
from enum import IntEnum, auto
from ..sharedManager import SharedManager
import time
from ..camera.cameraProcessorNodding import GestureTypes
from .shared.writer import ScreenWriter

class NoddingManager(SharedManager):
    file = "instance/nodding.json"

    # class State(IntEnum):
    #     keyboard = auto()
    #     camera = auto()
    #     web = auto()

    def __init__(self, screen):
        self.screen = screen
        self.writer = ScreenWriter(self.screen)
        self.camera = None
        super().__init__()
        
    # def getVars(self):
    #     return {
    #         'inputType': {
    #             'name': "Use Camera Input", 'type': 'I',
    #             'type': 'I', 'control': 'radio',
    #             'value': self.InputTypes.camera.value,
    #             'options': {i.name: i.value for i in self.InputTypes}
    #         },
    #     }
        
    def getCurrentGesture(self):
        if  self.camera:
            return self.camera.getValue('output.gesture')
        
        
    def proposeBottle(self, nr = None):
        logging.debug(f'Proposing Bottle {nr}')
        self.robot.turn(nr, 10)

    def run(self):
        self.camera = self.modules['camera']
        self.robot = self.modules['robot']
        
        while (True):
            gesture = self.getCurrentGesture()
            gestureName = GestureTypes(gesture).name
            # logging.debug(f'Gesture: {gesture} {gestureName}')
            
            self.screen.refresh()
            
            self.writer.addSigns((3, 3), f"NODDING MANAGER")
            
            self.writer.addSigns((3, 5), f"    Gesture: {gestureName}     ")
            self.writer.addSigns((3, 6), f"Robot State: {self.robot.State(self.robot.state).name}     ")
            # self.writer.addSigns((7, 5), gesture)
            
            self.screen.refresh()
            
            keyPressed = self.screen.getch()
            
            if keyPressed == ord('q'):
                break
            
            
            time.sleep(0.1)
            
            
        # self.game = RobotCameraGame(screen=self.screen, camera=self.modules['camera'],
        #                             robot=self.modules['robot'], manager=self)

        # # TODO INFORM AND REDO
        # config.getValue = SpaceInvadersManager.getConfigValue
        # SpaceInvadersManager.instance = self

        # self.game.run()
