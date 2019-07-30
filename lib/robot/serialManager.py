import logging
import serial
import time
import serial.tools.list_ports as list_ports
#from enum import IntEnum, auto
from ..multiManager import MultiManager

log = logging.getLogger("serial")

class SerialManager(MultiManager):
    file = "instance/serial.json"

    # speed = [
    #       9600,
    #      14400,
    #      19200,
    #      28800,
    #      38400,
    #      57600,
    #     115200
    # ]

    def __init__(self):
        self.ports = [p[0] for p in serial.tools.list_ports.comports()]
        self.ports.append('')
        self.serialBuffer = ''
        super().__init__(type='thread')

    def getVars(self):
        vars = {
            'init': {
                'port': {
                    'name': "Serial Port",
                    'type': 'I', 'control': 'combo',
                    'value': 0,
                    'options': {r: i for i, r in enumerate(self.ports)}
                },
                # 'speed': {
                #     'name': "Speed",
                #     'type': 'I', 'control': 'combo',
                #     'value': 6,
                #     'options': {r: r for r in self.speed}
                # }
            },
        }
        vars.update(super().getVars())
        return vars

    def getDisplayVars(self):
        return {
            'init': [
                'init.port',
                #'init.speed'
            ]
        }

    def prepare(self):
        port = self.ports[self.getValue('init.port')]
        log.debug('CONNECTING TO SERIAL PORT %s' % port)
        self.serialConn = serial.Serial(port=port, timeout = 0) # timeout = 0

    def write(self, message):
        try:
            self.serialConn.write((message + '\r\n').encode('ascii'))
            log.debug("T %s \\r\\n" % message)
            self.serialConn.flushInput()
        except Exception as e:
            log.info(str(e) + '\n')

    def loopStart(self):
        pass

    def loopMain(self):
        toRead = self.serialConn.inWaiting()
        if toRead > 0: #if incoming bytes are waiting to be read from the serial input buffer
            read = self.serialConn.read(toRead).decode('ascii')
            log.debug('READ SERIAL: "%s"' % read)

            if self.modules['web']:
                self.modules['web'].emit('serial.read', read)

            self.serialBuffer += read
            lines = self.serialBuffer.split('\r\n')
            self.serialBuffer = lines.pop()

            if self.modules['robot']:
                for line in lines:
                    self.modules['robot'].processLine(line)

    def loopEnd(self):
        self.serial.close()
