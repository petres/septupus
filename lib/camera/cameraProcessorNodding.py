import cv2
import numpy as np
from enum import IntEnum, auto
import logging
from collections import deque
from ..sharedManager import SharedManager
import sys

from noddingpigeon.model import make_model
from mediapipe.python.solutions import drawing_utils as mp_drawing
from mediapipe.python.solutions import face_detection as mp_face
from noddingpigeon.inference import postprocess

class GestureTypes(IntEnum):
    nodding = 0
    turning = 1
    stationary = 2
    undefined = 3


class CameraProcessor(object):
    vars = {
        'motion_threshold': {
            'name': "motion_threshold",
            'type': 'f', 'control': 'range',
            'min': 0, 'max': 1,
            'value': 0.7,
        },
        'gesture_threshold': {
            'name': "gesture_threshold",
            'type': 'f', 'control': 'range',
            'min': 0, 'max': 1,
            'value': 0.8,
        },
    }
    
    output = {
        'gesture': {
            'name': "gesture",
            'type': 'I', 'control': 'radio',
            'value': GestureTypes.undefined,
            'options': {i.name: i.value for i in GestureTypes}
        },
    }

    def __init__(self, camParams, params):
        self.resolution = camParams['resolution']
        self.featuresLastFrames = deque(maxlen = 60)
        self.stdout = sys.stdout
        self.stdout_noddingpigeon = open('log/noddingpigeon.log', 'w')
        
        self.model = make_model()
        
    
    def __del__(self):
        self.stdout_noddingpigeon.close()
    
    @classmethod
    def image2landmarks(cls, bgr_frame):
        with mp_face.FaceDetection(
            model_selection = 0, min_detection_confidence = 0.5
        ) as face_detection:
            frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)  # pylint: disable=no-member
            result = face_detection.process(frame)

            if result and result.detections and len(result.detections) == 1:
                detection = result.detections[0]

                right_eye_rel = mp_face.get_key_point(detection, mp_face.FaceKeyPoint.RIGHT_EYE)
                left_eye_rel = mp_face.get_key_point(detection, mp_face.FaceKeyPoint.LEFT_EYE)
                nose_tip_rel = mp_face.get_key_point(detection, mp_face.FaceKeyPoint.NOSE_TIP)
                mouth_center_rel = mp_face.get_key_point(detection, mp_face.FaceKeyPoint.MOUTH_CENTER)
                right_ear_rel = mp_face.get_key_point(detection, mp_face.FaceKeyPoint.RIGHT_EAR_TRAGION)
                left_ear_rel = mp_face.get_key_point(detection, mp_face.FaceKeyPoint.LEFT_EAR_TRAGION)

                face_box_rel = detection.location_data.relative_bounding_box
                face_box_rel = [
                    max(0.0, face_box_rel.xmin),
                    max(0.0, face_box_rel.ymin),
                    face_box_rel.width,
                    face_box_rel.height,
                ]
                xs = [
                    right_eye_rel.x,
                    left_eye_rel.x,
                    nose_tip_rel.x,
                    mouth_center_rel.x,
                    right_ear_rel.x,
                    left_ear_rel.x,
                ]
                ys = [
                    right_eye_rel.y,
                    left_eye_rel.y,
                    nose_tip_rel.y,
                    mouth_center_rel.y,
                    right_ear_rel.y,
                    left_ear_rel.y,
                ]
                
                return {
                    'valid': True,
                    'features': [*face_box_rel, *xs, *ys],
                    'detection': detection,
                }
        
        return {'valid': False}


    def evaluate(self, frame, params):
        r = {
            'output': {},
            'images': {},
        }
        
        # print(params)
        
        landmarks = self.image2landmarks(frame)

        if params['control.showImage'] != 'off':
            r['images']['org'] = frame
        

        
        if landmarks['valid']:
            if params['control.overlay'] == 1:
                mp_drawing.draw_detection(frame, landmarks['detection'])
                r['images']['overlay'] = frame
            # print(features)
            
            self.featuresLastFrames.append(landmarks['features'])
        
            # logging.debug(f'Deque size: {len(self.featuresLastFrames)}, Len features: {len(features)}')
            
            if len(self.featuresLastFrames) == 60:
                # landmarks = video_to_landmarks(video_path)
                sys.stdout = self.stdout_noddingpigeon
                prediction = self.model.predict(np.expand_dims(self.featuresLastFrames, axis=0))[0].tolist()
                sys.stdout = self.stdout
                
                
                output = postprocess(prediction, params['motion_threshold'], params['gesture_threshold'])
                
                # logging.debug(f'Output: {output["gesture"]}')
                
                r['output']["gesture"] = GestureTypes.undefined
                
                if output["gesture"] == 'nodding':
                    r['output']["gesture"] = GestureTypes.nodding
                    
                if output["gesture"] == 'turning':
                    r['output']["gesture"] = GestureTypes.turning
                
                if output["gesture"] == 'stationary':
                    r['output']["gesture"] = GestureTypes.stationary
                
                
                for i in range(30):
                    self.featuresLastFrames.popleft()
                
                # self.featuresLastFrames.clear()

        return r


    