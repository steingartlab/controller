import json
from time import sleep

import flask
from werkzeug.exceptions import BadRequest

from controller import controller, logger, utils

with open('docker.json', 'r') as json_file:
    containers = json.load(json_file)


HOST = utils.make_ip(containers['remotecontrol']['ip'])
PORT = containers['remotecontrol']['port']

logger.configure()
app: flask.Flask = flask.Flask(__name__)
controller_: controller.Controller = controller.Controller()


def configure_routes(app):

    @app.route('/')
    def hello_world():
        return f'Controller is up. Status: {status()}'


    @app.route('/last_updated')
    def last_updated():
        return str(controller_.last_updated)


    @app.route('/pulse', methods=['POST'])
    def pulse():
        waveform = controller.pulse(incoming=flask.request.values.to_dict())

        return json.dumps(waveform)


    @app.route('/start', methods=['POST'])
    def start():
        controller.start_thread(
            controller_=controller_,
            incoming=flask.request.values.to_dict()
        )
        sleep(2)  # To ensure correct status message is returned

        return status()


    @app.route('/status')
    def status():
        return str(controller_.status)


    @app.route('/stop')
    def stop():
        controller_.stop()

        return status()


    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return '', 404


configure_routes(app)


if __name__ == '__main__':
    app.run(port=PORT, host=HOST, debug=False)
