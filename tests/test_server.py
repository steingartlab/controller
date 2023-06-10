from dataclasses import asdict
import json
import os

import flask
from flask.testing import FlaskClient
import pytest

import server
from controller import picoscope

pulsing_params = picoscope.PicoParams(10, 1, 10)
INITIAL_STATUS = 'Controller is up. Status: not_started'

@pytest.fixture
def client():
    app = flask.Flask(__name__)
    server. configure_routes(app)
    client = app.test_client()

    return client


def test_base_route(client: FlaskClient):
    response = client.get('/')

    assert response.status_code == 200
    assert response.get_data().decode() == INITIAL_STATUS


def test_random_route_failure(client: FlaskClient):
    response = client.get('/some_nonexistent_url')
    assert response.status_code == 404


def test_logs():
    assert os.path.isfile('logs/logs.log')


def test_pulse(client):
    response = client.post(
        '/pulse',
        data=asdict(pulsing_params)
    )
    waveform = json.loads(response.get_data())

    assert isinstance(waveform, dict)
    assert isinstance(waveform['amps'], list)
    assert isinstance(waveform['amps'][0], list)
    assert isinstance(waveform['amps'][0][0], float)

def test_last_updated(client):
    response = client.get('/last_updated').text

    assert isinstance(response, str)
    # http returns floats as strings. This ensures that the
    # response can be converted to a float
    assert isinstance(float(response), float) 


def test_status(client):
    response = client.get('/status').text
    assert response == 'not_started'

# def test_start():