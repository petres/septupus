from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    current_app, send_from_directory, send_file, Response, jsonify
)
import time
bp = Blueprint('camera', __name__, url_prefix='/camera')
cam = None

@bp.route('/stop')
def stop():
    cam.stop()
    return jsonify({
        'valid': True
    })

@bp.route('/start')
def start():
    cam.start()
    return jsonify({
        'valid': True
    })

@bp.route('/image')
def image():
    if cam.isRunning() and cam.getValue('control.showImage') != cam.ImageTypes.off:
        return Response(cam.getFrame(),
                        mimetype='image/jpeg')

# @bp.route('/feed')
# def feed():
#     if cam.isRunning() and cam.getValue('control.showImage') != cam.ImageTypes.off:
#         return Response(getFrame(),
#                         mimetype='multipart/x-mixed-replace; boundary=frame')
#
# def getFrame():
#     while cam.isRunning() and cam.getValue('control.showImage') != cam.ImageTypes.off:
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + cam.getFrame() + b'\r\n')
