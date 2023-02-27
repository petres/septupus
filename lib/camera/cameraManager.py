import cv2
import numpy as np
import logging
from multiprocessing import Array
from enum import IntEnum, auto
# from .cameraProcessorPositionShoot import CameraProcessor
from .cameraProcessorNodding import CameraProcessor, GestureTypes
from ..multiManager import MultiManager



class CameraManager(MultiManager):
    file = "instance/camera.json"

    class ImageTypes(IntEnum):
        off = auto()
        org = auto()
        # overlay = auto()
        
        # TODO: move to processor
        # gray = auto()
        # thresh = auto()

    resolutions = [
        (160, 120),
        (180, 320),
        (240, 320)
    ]

    def __init__(self):
        self.processor = CameraProcessor
        super().__init__()

    def getVars(self):
        vars = {
            'init': {
                'device': {
                    'type': 'I',
                    'value': 0
                },
                'resolution': {
                    'type': 'I', 'control': 'radio',
                    'value': 0,
                    'options': {r: i for i, r in enumerate(self.resolutions)}
                }
            },
            'control': {
                'showImage': {
                    'name': "Display Image",
                    'type': 'I', 'control': 'radio',
                    'value': self.ImageTypes.org.value,
                    'options': {i.name: i.value for i in self.ImageTypes}
                },
                'overlay': {
                    'name': "Display Image Overlay",
                    'type': 'I', 'control': 'radio',
                    'value': 0,
                    'options': {i.name: i.value for i in self.OnOffFlags}
                }
            },
            'output': {
                # 'position': {
                #     'name': "Position",
                #     'type': 'f',
                #     'value': 0.5
                # },
                # 'shootFlag': {
                #     'name': "Shoot Flag",
                #     'type': 'b',
                #     'value': 0
                # },
                'gesture': {
                    'name': "gesture",
                    'type': 'I', 'control': 'radio',
                    'value': GestureTypes.undefined,
                    'options': {i.name: i.value for i in GestureTypes}
                },
            },

            'processor': self.processor.vars
        }
        vars.update(super().getVars())
        return vars

    def getDisplayVars(self):
        return {
            'control': [
                'multi.sleep',
                'control.showImage',
                'control.overlay',
            ],
            'processor': ['processor.' + i for i in self.vars['processor'].keys()],
            'output': [
                'output.gesture',
                # 'output.position',
                # 'output.shootFlag',
            ]
            
        }

    def prepare(self):
        self.initParams = {
            'device': self.getValue('init.device'),
            'resolution': self.resolutions[self.getValue('init.resolution')],
        }
        self.image = Array('B', self.initParams['resolution'][0] * self.initParams['resolution'][1]*3)

    def loopPrepare(self):
        logging.info('CAMERA INIT: %s' % self.initParams)
        self.cap = cv2.VideoCapture(self.initParams['device'])
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.initParams['resolution'][0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.initParams['resolution'][1])
        params = {k: self.getValue('processor.' + k) for k, v in self.vars['processor'].items()}
        self.cp = self.processor(self.initParams, params)

    def loopMain(self):
        ret, frame = self.cap.read()
        params = {k: self.getValue('processor.' + k) for k, v in self.vars['processor'].items()}
        imageType = self.ImageTypes(self.getValue('control.showImage')).name
        params['control.showImage'] = imageType
        params['control.overlay'] = 'overlay' in self.getVars()['control'] and self.getValue('control.overlay') == 1
        o = self.cp.evaluate(frame, params)

        if 'output' in o:
            output = o['output']
            # logging.debug(f'Output: {output}')
            for k in output.keys():
                if output[k] is not None:
                    self.setValue('.'.join(['output', k]), output[k])

        if imageType != "off":
            images = o['images']
            i = images[imageType]
            if params['control.overlay'] and 'overlay' in images:
                overlay = images['overlay']
                cnd = (overlay[:, :, 0] + overlay[:, :, 1] + overlay[:, :, 2]) > 0
                i[cnd] = overlay[cnd]
            self.image[:] = i.flatten().astype(np.uint8)


    def loopCleanup(self):
        self.cap.release()

    def getFrame(self):
        dims = (self.initParams['resolution'][1], self.initParams['resolution'][0], 3)
        frame = np.frombuffer(self.image.get_obj(), dtype=np.uint8).reshape(dims)
        ret, buffer = cv2.imencode(".jpg", frame)
        return buffer.tobytes()
