import cv2
import numpy as np
from enum import IntEnum, auto
import logging
from collections import deque


class CameraProcessor(object):
    vars = {
        'threshold': {
            'name': "Threshold",
            'type': 'I', 'control': 'range',
            'min': 0, 'max': 255,
            'value': 200
        },
        'blurRadius': {
            'name': "Blur Radius",
            'type': 'I', 'control': 'range',
            'min': 0, 'max': 100,
            'value': 0
        },
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
            'name': "Shoot Height",
            'type': 'I', 'control': 'range',
            'min': 0, 'max': 20,
            'value': 5
        },
        'margin': {
            'name': "Margin",
            'type': 'I', 'control': 'range',
            'min': 0, 'max': 20,
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

    def evaluate(self, frame, params):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        position = None
        shootFlag = None
        avg = None

        blurRadius = params['blurRadius']
        if blurRadius == 0:
            blurred = gray
        else:
            blurRadius = blurRadius - blurRadius%2 + 1
            blurred = cv2.GaussianBlur(gray, (blurRadius, blurRadius), 0)

        thresh = cv2.threshold(blurred, params['threshold'], 255, cv2.THRESH_BINARY)[1]
        #thresh = cv2.erode(thresh, None, iterations=2)
        #thresh = cv2.dilate(thresh, None, iterations=4)
        m = cv2.moments(thresh)
        if m['m00'] != 0:
            #print("x = " + str(m['m10']/m['m00']))
            #print("y = " + str(m['m01']/m['m00']))
            tmpX = m['m10']/m['m00']
            tmpX01 = tmpX/self.resolution[0]

            tmpY = m['m01']/m['m00']
            tmpY01 = tmpY/self.resolution[1]

            self.slidingWindowShoot.append(tmpY01)
            if len(self.slidingWindowShoot) > params['slidingWindowShootSize']:
                self.slidingWindowShoot.popleft()
            sortList = sorted(self.slidingWindowShoot)
            avg = sortList[int(len(self.slidingWindowShoot) / 2)]
            if tmpY01 < avg - 0.01*params['shootHeight']:
                #print "SHOOT"
                shootFlag = 1
            else:
                shootFlag = 0

            if params['slidingWindowSize'] > 1:
                self.slidingWindow.popleft()
                self.slidingWindow.append(tmpX01)
                sortList = sorted(self.slidingWindow)
                position = sortList[int(params['slidingWindowSize'] / 2)]
            else:
                position = tmpX01

        r = {
            'position': position,
            'shootFlag': shootFlag
        }

        if params['control.showImage'] != 'off':
            overlay = np.zeros((self.resolution[1], self.resolution[0], 3))
            offset = int(0.01 * params['margin'] * self.resolution[0])

            cv2.line(overlay, (offset, 0), (offset, self.resolution[1]), (255, 0, 0), 2)
            cv2.line(overlay, (self.resolution[0] - offset, 0), (self.resolution[0] - offset, self.resolution[1]), (255,0,0), 2)

            if m['m00'] != 0:
                cv2.circle(overlay, (int(tmpX), int(tmpY)), 5, (0, 255, 0), -1)

            if avg is not None:
                h = int((avg - 0.01*params['shootHeight'])*self.resolution[1])
                cv2.line(overlay, (int(tmpX) - 20, h), (int(tmpX) + 20, h), (0, 0, 255), 2)

            if position is not None:
                cv2.circle(overlay, (int(position * self.resolution[0]), self.resolution[1] - 10), 5, (0, 0 ,255), -1)

            r['images'] = {
                'org': frame,
                'gray': cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
                'thresh': cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR),
                'overlay': overlay,
            }

        return r
