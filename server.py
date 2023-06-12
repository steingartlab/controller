import json
import logging
import os
import threading

import flask
from werkzeug.exceptions import BadRequest

import config
from controller import controller

log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s: %(message)s'
)

app: flask.Flask = flask.Flask(__name__)
controller_: controller.Controller = controller.Controller()

def configure_routes(app):

    @app.route('/')
    def hello_world():
        """
        Returns:
            Str: Status message
        """
        return f'Controller is up. Status: {status()}'


    @app.route('/last_updated')
    def last_updated():
        return str(controller_.last_updated)


    @app.route('/pulse', methods=['POST'])
    def pulse():
        waveform = controller.pulse(incoming=flask.request.values.to_dict())
        print(waveform)

        return json.dumps(waveform)


    @app.route('/start', methods=['POST'])
    def start():
        controller.start_thread(
            controller_=controller_, incoming=flask.request.values.to_dict()
        )

        return status()


    @app.route('/status')
    def status():
        return controller_.status


    @app.route('/stop')
    def stop():
        controller_.stop()

        return controller_.status


    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return '', 404


configure_routes(app)


if __name__ == '__main__':
    app.run(
        port=config.server['port'],
        host=config.server['ip'],
        debug=False
    )
