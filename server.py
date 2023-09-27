import json
import threading
from time import sleep

import flask
from werkzeug.exceptions import BadRequest

from remotecontrol import controller, logger, utils


with open('docker.json', 'r') as json_file:
    containers = json.load(json_file)


HOST = utils.make_ip(containers['remotecontrol']['ip'])
PORT = containers['remotecontrol']['port']

logger.configure()
app: flask.Flask = flask.Flask(__name__)

controller_: controller.Controller = controller.Controller()
thread = threading.Thread(target=controller.Controller.loop, args=(controller_))
thread.start()


def configure_routes(app):

    @app.route('/')
    def hello_world():
        return 'RemoteControl is up.'


    # @app.route('/last_updated', methods=['POST'])
    # def last_updated():
    #     jig_name = flask.request.json()

    #     return controller_.jigs[jig_name].last_updated


    # @app.route('/pulse', methods=['POST'])
    # def pulse():
    #     waveform = controller.pulse(incoming=flask.request.values.to_dict())

    #     return json.dumps(waveform)


    @app.route('/start', methods=['POST'])
    def start():
        payload = flask.request.json()
        jig = payload['jig']

        return controller_.jigs[jig].start(payload)


    @app.route('/status', methods=['POST'])
    def status():
        jig_name = flask.request.json()

        return controller_.jigs[jig_name].status


    # @app.route('/available_jigs', methods=['POST'])
    # def status():
    #     jig_name = flask.request.json()

    #     return jigs.


    @app.route('/stop', methods=['POST'])
    def stop():
        jig_name = flask.request.json()
        controller_.jigs[jig_name].stop()
        sleep(2)

        return status()


    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return '', 404


configure_routes(app)


if __name__ == '__main__':
    app.run(port=PORT, host=HOST, debug=False)
