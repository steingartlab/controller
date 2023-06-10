import logging
import os
import threading

import flask
from werkzeug.exceptions import BadRequest

import config
from controller import controller
from controller.picoscope import PicoParams


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
        incoming = flask.request.values.to_dict()
        pico_params: PicoParams = PicoParams(**incoming)

        return controller_.pulse(pico_params)


    @app.route('/start', methods=['POST'])
    def start():
        incoming = flask.request.values.to_dict()
        exp_settings = controller.Settings(**incoming)
        pico_params = PicoParams(**incoming)
        thread = threading.Thread(
            target=controller_.start,
            args=(exp_settings, pico_params)
        )
        thread.start()

        return status()


    @app.route('/status')
    def status():
        return controller_.status


    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return '', 404


configure_routes(app)


if __name__ == '__main__':
    app.run(
        port=config.server['PORT'],
        host=config.server['IP'],
        debug=False
    )
