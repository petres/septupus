import logging
#from enum import IntEnum, auto
from ..multiManager import MultiManager
from ..games.spaceInvaders.config import config
from queue import Queue
from enum import IntEnum, auto

log = logging.getLogger("robot")

class RobotManager(MultiManager):
    file = "instance/robot.json"

    class State(IntEnum):
        ready = auto()
        readyCup= auto()
        pouring = auto()
        bottleEmpty = auto()
        error = auto()
        unknown = auto()

    def __init__(self):
        self.ingredients = list(config.getValue('ingredients.beverages').keys())
        self.ingredients.append('NONE')
        self.state = self.State.unknown
        self.pourQueue = Queue()
        super().__init__()

    def getVars(self):
        vars = {
            'assignment': {
            },
            'mixing': {
                'portion': {
                    'name': "Portion",
                    'type': 'I', 'control': 'range',
                    'min': 10, 'max': 50,
                    'value': 25
                },
                'volume': {
                    'name': "Volume",
                    'type': 'I', 'control': 'range',
                    'min': 100, 'max': 500,
                    'value': 200
                }
            },
        }

        options = {r: i for i, r in enumerate(self.ingredients)}
        assignmentTemplate = {
            'name': "Bottle %s",
            'type': 'I', 'control': 'combo',
            'value': 0,
            'options': options
        }

        for i in range(7):
            a = assignmentTemplate.copy()
            a['name'] = a['name'] % (i + 1)
            vars['assignment']['a%s' % (i + 1)] = a

        return vars

    def getDisplayVars(self):
        return {
            'assignment': ['assignment.' + i for i in self.vars['assignment'].keys()],
            'mixing': [
                'mixing.portion',
                'mixing.volume',
            ]
        }

    def getAvailableIngredients(self):
        ingredients = []
        for id in ['assignment.' + i for i in self.vars['assignment'].keys()]:
            v = self.ingredients[self.getValue(id)]
            if v != 'NONE':
                ingredients.append(v)
        #log.info(ingredients)
        return set(ingredients)

    def getPortForIngredient(self, ingredient):
        for i, id in enumerate(['assignment.' + i for i in self.vars['assignment'].keys()]):
            if self.ingredients[self.getValue(id)] == ingredient:
                return i
        raise Exception('Ingredient %s not available!' % ingredient)

    def prepare(self):
        self.state = self.State.unknown
        self.pourQueue = Queue()

    def send(self, verb, *args):
        message = "%s %s" % (verb, " ".join(str(n) for n in args))
        if self.modules['serial']:
            self.modules['serial'].write(message)

    def processLine(self, line):
        commandList = line.split(" ")
        if commandList[0] == "READY":
            if int(commandList[2]) == 1:
                self.state = self.State.readyCup
            else:
                self.state = self.State.ready
        elif commandList[0] == "WAITING_FOR_CUP":
            pass
        elif commandList[0] == "POURING":
            pass
        elif commandList[0] == "ENJOY":
            pass
            # if self.State.bottleEmpty:
            #     self.state = self.State.bottleEmpty
                #self.listenCallback("bottleEmptyResume")
        elif commandList[0] == "ERROR":
            if commandList[1] == "BOTTLE_EMPTY":
                self.state = self.State.bottleEmpty
                #self.listenCallback("bottleEmpty")
        elif commandList[0] == "NOP":
            pass
        else:
            pass

        if self.modules['spaceInvaders']:
            self.modules['spaceInvaders'].robotStateUpdate(self.state)
        #self.listenCallback(command)

        # if not self.pourQueue.empty() and self.state == self.State.readyCup:
        #     self.pour(*self.pourQueue.get())

        # elif self.input == ord('l'):
        #     if game.cupThere:
        #         game.robotMessage("cupNotThere")
        #     else:
        #         game.robotMessage("cupThere")
        #
        # if self.input == ord('r') or (not game.gameStarted and game.cupThere and game.cupTaken):
        #     game.prepare()


    def pourBottle(self, bottleNr, amount):
        temp = [0] * 7
        temp[bottleNr] = amount
        self.pourQueue.put(temp)
        # self.pour(*temp)

    def pourIngredient(self, ingredient, amount):
        try:
            port = self.getPortForIngredient(ingredient)
            log.info('Pouring %s from %s' % (ingredient, port))
            self.pourBottle(port, amount)
        except Exception as e:
            log.warning(e)

    def pour(self, *args):
        log.info(
            "INFO: SEND POUR COMMAND (" + " ".join(str(n) for n in args) + ")")
        """pour x_i grams of ingredient i, for i=1..n; will skip bottle
		if x_n < UPRIGHT_OFFSET"""
        # TODO: Check if ready for pour
        # from time import sleep
        # sleep(5)
        self.send("POUR", *args)
        # self.pouring = True

    def abort(self):
        """abort current cocktail"""
        self.state = self.State.unknown
        self.send("ABORT")

    def resume(self):
        """resume after BOTTLE_EMPTY error, use this command when
        bottle is refilled"""
        self.send("RESUME")

    def dance(self):
        """let the bottles dance!"""
        self.send("DANCE")

    def tare(self):
        """sets scale to 0, make sure nothing is on scale when
        sending this command Note: taring is deleled, when Arduino
        is reseted (e.g. on lost serial connection)"""
        self.send("TARE")

    def turn(self, bottle_nr, microseconds):
        """turns a bottle (numbered from 0 to 6) to a position
        given in microseconds"""
        self.send("TURN")

    def echo(self, msg):
        """Example: ECHO ENJOY\r\n Arduino will then print "ENJOY"
        This is a workaround to resend garbled messages manually."""
        self.send("ECHO", msg)

    def nop(self):
        """Arduino will do nothing and send message "DOING_NOTHING".
        This is a dummy message, for testing only."""
        self.send("NOP")
