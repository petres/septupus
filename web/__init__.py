import os, json
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from .modules import camera


def start_app(modules):
    # create and configure the app
    app = Flask(__name__,
        instance_relative_config=True,
    )
    app.config.from_pyfile('./config.py', silent=True)

    camera.cam = modules['camera']
    app.register_blueprint(camera.bp)
    socketio = SocketIO(app)
    #app.add_url_rule('/', endpoint='index')

    @app.context_processor
    def manifest():
        manifest_filename = os.path.join(app.static_folder, 'manifest.json')
        with open(manifest_filename) as manifest_file:
            return dict(manifest=json.load(manifest_file))


    @app.route('/')
    def index():
        return render_template('index.html.j2', modules = modules, activeModule = 'robot')


    # @socketio.on('connect')
    # def test_connect():
    #     emit('after connect',  {'data':'Lets dance'})


    @socketio.on('generic-update')
    def value_changed(d):
        modules[d['module']].setValue(d['name'], d['value'])
        # emit('update value', message, broadcast=True)

    @socketio.on('param update')
    def value_changed(d):
        modules[d['module']].setValue(d['name'], d['value'])

    socketio.run(app)
