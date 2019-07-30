import cv2
import numpy as np
from enum import IntEnum, auto
import logging
from collections import deque
from ..sharedManager import SharedManager

class CameraProcessor(object):
    vars = {
        'threshold': {
            'name': "Threshold",
            'type': 'I', 'control': 'range',
            'min': 0, 'max': 255,
            'value': 200
        },
        # 'blurRadius': {
        #     'name': "Blur Radius",
        #     'type': 'I', 'control': 'range',
        #     'min': 0, 'max': 100,
        #     'value': 0
        # },
        'slidingWindowSize': {
            'name': "Sliding Window Size (Position)",
            'type': 'I', 'control': 'range',
            'min': 0, 'max': 20,
            'value': 5
        },
        'slidingWindowShootSize': {
            'name': "Sliding Window Size (Shoot)",
            'type': 'I', 'control': 'range',
            'min': 0, 'max': 20,
            'value': 9
        },
        'shootHeight': {
            'name': "Shoot Height Offset (%)",
            'type': 'I', 'control': 'range',
            'min': 0, 'max': 20,
            'value': 5
        },
        'mirror': {
            'name': "Mirror",
            'type': 'I', 'control': 'radio',
            'value': 0,
            'options': {i.name: i.value for i in SharedManager.OnOffFlags}
        },
        'margin': {
            'name': "Margin (%)",
            'type': 'I', 'control': 'range',
            'min': 0, 'max': 50,
            'value': 5
        },
    }


    def __init__(self, camParams, params):
        self.resolution = camParams['resolution']

        if params['slidingWindowSize'] > 0:
            self.slidingWindow = deque()
            for i in range(params['slidingWindowSize']):
                self.slidingWindow.append(0.5)

        self.slidingWindowShoot = deque()

    @classmethod
    def addToQueueAndGetMedian(cls, queue, value, size):
        queue.append(value)
        if len(queue) > size:
            queue.popleft()
        sortList = sorted(queue)
        return sortList[int(len(queue) / 2)]


    def evaluate(self, frame, params):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        width, height = self.resolution

        position = None
        shootFlag = False

        smyr = None
        marginF = params['margin']/100
        shootHeightF = params['shootHeight']/100

        # blurRadius = params['blurRadius']
        # if blurRadius == 0:
        #     blurred = gray
        # else:
        #     blurRadius = blurRadius - blurRadius%2 + 1
        #     blurred = cv2.GaussianBlur(gray, (blurRadius, blurRadius), 0)
        # thresh = cv2.threshold(blurred, params['threshold'], 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.threshold(gray, params['threshold'], 255, cv2.THRESH_BINARY)[1]

        #thresh = cv2.erode(thresh, None, iterations=2)
        #thresh = cv2.dilate(thresh, None, iterations=4)
        m = cv2.moments(thresh)

        if m['m00'] != 0:
            mx = m['m10']/m['m00']
            mxr = mx/width

            my = m['m01']/m['m00']
            myr = my/height

            smyr = self.addToQueueAndGetMedian(self.slidingWindowShoot, myr, params['slidingWindowShootSize'])
            shootFlag = myr < smyr - shootHeightF

            if params['slidingWindowSize'] > 1:
                smxr = self.addToQueueAndGetMedian(self.slidingWindow, mxr, params['slidingWindowSize'])
            else:
                smxr = mxr

            position = (smxr - marginF)/(1 - 2 * marginF)
            position = min(1, max(position, 0))

            if params['mirror'] == 1:
                position = 1 - position

        r = {
            'output': {
                'position': position,
                'shootFlag': shootFlag
            }
        }

        if params['control.showImage'] != 'off':
            overlay = np.zeros((height, width, 3))
            marginP = int(width * marginF)

            cv2.line(overlay, (marginP, 0), (marginP, height), (255, 0, 0), 2)
            cv2.line(overlay, (width - marginP, 0), (width - marginP, height), (255,0,0), 2)

            if m['m00'] != 0:
                cv2.circle(overlay, (int(mx), int(my)), 5, (0, 255, 0), -1)

            if smyr is not None:
                h = int((smyr - shootHeightF) * height)
                cv2.line(overlay, (int(mx) - 20, h), (int(mx) + 20, h), (0, 0, 255), 2)

            if position is not None:
                t = position*(1 - 2*marginF)
                cv2.circle(overlay, (int((t + marginF)*width), height - 10), 5, (0, 0, 255), -1)

            r['images'] = {
                'org': frame,
                'gray': cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
                'thresh': cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR),
                'overlay': overlay,
            }

        return r
