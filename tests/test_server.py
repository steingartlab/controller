import pytest

import flask
from flask.testing import FlaskClient

import server

payload = {
    'jig': 'pikachu',
    'exp_id': 'test_x',
    'picoscope': {'delay': 10, 'duration': 10, 'avg_num': 8, 'voltage_range': 1},
    'pulser': {'gain_dB': 30},
}


@pytest.fixture
def base_client():
    app = flask.Flask(__name__)
    server.configure_routes(app)
    client = app.test_client()

    return client


def test_base(base_client: FlaskClient):
    response = base_client.get('/')

    assert response.status_code == 200  
    assert response.text == 'RemoteControl is up.'


@pytest.fixture
def base_client_with_teardown(base_client: FlaskClient):
    yield base_client

    base_client.post('/stop', json=payload['jig'])


def test_start(base_client_with_teardown: FlaskClient):
    response = base_client_with_teardown.post('/start', json=payload['jig'])

    assert response.status_code == 200  
    assert response.text == 1


@pytest.fixture
def running_client(base_client: FlaskClient):
    base_client.post('/start', json=payload['jig'])

    return base_client


def test_stop(running_client: FlaskClient):
    response = running_client.post('/stop', json=payload['jig'])

    assert response.status_code == 200  
    assert response.text == 2


def test_status_not_started(base_client):
    response = base_client.post('/status', json=payload['jig'])

    assert response.status_code == 200  
    assert response.text == 0


# @pytest.fixture
# def started_client(base_client: FlaskClient):
#     yield base_client.post('/start', json=payload['jig'])

    
# def test_status_running(base_client):
#     response = base_client.post('/status', json=payload['jig'])

