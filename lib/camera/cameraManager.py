import cv2
from multiprocessing import Process, Value, Array
from enum import IntEnum, auto
import numpy as np
import time
import logging
from .cameraProcessor import CameraProcessor
from ..sharedManager import SharedManager
from ..processManager import ProcessManager


class CameraManager(SharedManager, ProcessManager):
    class ImageTypes(IntEnum):
        off = auto()
        org = auto()
        gray = auto()
        thresh = auto()
        overlay = auto()

    resolutions = [
        (160, 120),
        (180, 320),
        (240, 320)
    ]

    def __init__(self):
        self.initVars()

    def getVars(self):
        return {
            'init': {
                'device': {
                    'type': 'I',
                    'value': 0
                },
                'resolution': {
                    'type': 'I',
                    'value': 0,
                    'control': 'radio',
                    'options': {r: i for i, r in enumerate(self.resolutions)}
                }
            },
            'control': {
                'showImage': {
                    'name': "Display Image",
                    'type': 'I',
                    'value': self.ImageTypes.org.value,
                    'control': 'radio',
                    'options': {i.name: i.value for i in self.ImageTypes}
                },
                'overlay': {
                    'name': "Display Image Overlay",
                    'type': 'I',
                    'value': 0,
                    'control': 'radio',
                    'options': {
                        "Off": 0,
                        "On": 1
                    }
                },
                'sleep': {
                    'name': "Sleep (ms)",
                    'type': 'I',
                    'control': 'range',
                    'min': 0,
                    'max': 1000,
                    'value': 10
                },
                'flag': {
                    'type': 'I',
                    'value': self.ControlFlags.run.value,
                    'control': 'radio',
                    'options': {i.name: i.value for i in self.ControlFlags}
                },
            },
            'output': {
                'position': {
                    'type': 'd',
                    'value': 0.5
                },
                'shootFlag': {
                    'type': 'b',
                    'value': 0
                }
            },
            'processor': CameraProcessor.vars
        }

    def getDisplayVars(self):
        return {
            'control': [
                'control.sleep',
                'control.showImage',
                'control.overlay'
            ],
            'processor': ['processor.' + i for i in self.vars['processor'].keys()]
        }

    def prepareProcess(self):
        self.initParams = {
            'device': self.getValue('init.device'),
            'resolution': self.resolutions[self.getValue('init.resolution')],
        }
        self.image = Array('B', self.initParams['resolution'][0] * self.initParams['resolution'][1]*3)

    def loopStart(self):
        logging.info('CAMERA INIT: %s' % self.initParams)
        self.cap = cv2.VideoCapture(self.initParams['device'])
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.initParams['resolution'][0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.initParams['resolution'][1])
        params = {k: self.getValue('processor.' + k) for k, v in self.vars['processor'].items()}
        self.cp = CameraProcessor(self.initParams, params)

    def loopMain(self):
        ret, frame = self.cap.read()
        params = {k: self.getValue('processor.' + k) for k, v in self.vars['processor'].items()}
        imageType = self.ImageTypes(self.getValue('control.showImage')).name
        params['control.showImage'] = imageType
        o = self.cp.evaluate(frame, params)
        if imageType != "off":
            i = o['images'][imageType]
            if self.getValue('control.overlay') == 1 and "overlay" in o['images']:
                overlay = o['images']['overlay']
                cnd = (overlay[:, :, 0] + overlay[:, :, 1] + overlay[:, :, 2]) > 0
                i[cnd] = overlay[cnd]
            self.image[:] = i.flatten().astype(np.uint8)
        time.sleep(self.getValue('control.sleep')/1000)

    def loopEnd(self):
        self.cap.release()

    def getFrame(self):
        dims = (self.initParams['resolution'][1], self.initParams['resolution'][0], 3)
        frame = np.frombuffer(self.image.get_obj(), dtype=np.uint8).reshape(dims)
        ret, buffer = cv2.imencode(".jpg", frame)
        return buffer.tobytes()
