from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    current_app, send_from_directory, send_file, Response, jsonify
)

bp = Blueprint('serial', __name__, url_prefix='/serial')

# @bp.route('/stop')
# def stop():
#     cam.stop()
#     return jsonify({
#         'valid': True
#     })
#
# @bp.route('/start')
# def start():
#     cam.start()
#     return jsonify({
#         'valid': True
#     })
