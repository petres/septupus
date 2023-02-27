import os, sys, json
import logging
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from .modules import camera, serial
import logging

logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('engineio.server').setLevel(logging.WARNING)
logging.getLogger('socketio.server').setLevel(logging.WARNING)

# TODO INFORM AND REDO
sys.path.append(os.path.join(os.path.dirname(sys.path[0]), '..'))

from lib.multiManager import MultiManager

class WebManager(MultiManager):
    file = "instance/web.json"

    def __init__(self):
        super().__init__(type='thread')

    def prepare(self):
        self.multi.setDaemon(True)
        # create and configure the app
        self.app = Flask(__name__,
            instance_relative_config=True,
        )
        # self.app.config.from_pyfile('./config.py', silent=True)

        camera.cam = self.modules['camera']
        serial.ser = self.modules['serial']

        self.app.register_blueprint(camera.bp)
        self.app.register_blueprint(serial.bp)

        self.socketio = SocketIO(self.app)
        #app.add_url_rule('/', endpoint='index')

        @self.app.context_processor
        def manifest():
            manifest_filename = os.path.join(self.app.static_folder, 'manifest.json')
            with open(manifest_filename) as manifest_file:
                return dict(manifest=json.load(manifest_file))

        @self.app.route('/')
        def index():
            return render_template('index.html.j2', modules=self.modules, activeModule='serial')

        @self.app.route('/play')
        def startGame():
            self.modules['spaceInvaders'].game.play()

        # @self.socketio.on('connect')
        # def test_connect():
        #     emit('after connect',  {'data':'Lets dance'})

        @self.socketio.on('generic.update')
        def generic_update(d):
            self.modules[d['module']].setValue(d['name'], d['value'])
            # emit('update value', message, broadcast=True)

        @self.socketio.on('generic.call')
        def generic_call(d):
            self.modules[d['module']].call(d['function'])
            # emit('update value', message, broadcast=True)

        @self.socketio.on('serial.send')
        def serial_write(d):
            self.modules['serial'].write(d['message'])
            # emit('update value', message, broadcast=True)

    def loop(self):
        self.socketio.run(self.app, host='0.0.0.0')

    def emit(self, channel, message):
        self.socketio.emit(channel, message)

    def stop(self):
        #self.socketio.stop()
        #self.socketio.server.stop()
        pass
