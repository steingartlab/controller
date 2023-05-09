import logging
import os
import threading

import flask
from werkzeug.exceptions import BadRequest

from controller import controller, instruments, utils


log_filename = "logs/logs.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s: %(message)s'
)

app: flask.Flask = flask.Flask(__name__)
PORT: int = 5002

controller_: controller.Controller = controller.Controller()

@app.route('/')
def hello_world():
    """
    Returns:
        Str: Status message
    """
    return 'Siberiaaaa the place to be'


@app.route('/status')
def status():
    return controller_.status


@app.route('/pulse', methods=['POST'])
def pulse():
    incoming_settings: dict[str, str] = flask.request.values.to_dict()
    pico_params: instruments.PicoParams = dataclass_from_dict(
        dataclass_=instruments.PicoParams,
        dict_=incoming_settings
    )
    waveform = controller_.pulse()

    return waveform


@app.route('/start', methods=['POST'])
def start():
    incoming_settings: dict[str, str] = flask.request.values.to_dict()
    settings: controller.Settings = utils.dataclass_from_dict(
        dataclass_=controller.Settings, 
        dict_=incoming_settings
    )
    settings.set_pico()
    thread = threading.Thread(target=controller_.loop, args=(settings))
    thread.start()

    return 'Experiment started'


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return '', 404


if __name__ == '__main__':
    app.run(port=PORT, host="0.0.0.0", debug=False)