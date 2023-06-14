import os

import pytest

from controller import picoscope, utils
from controller.controller import Status

IP = '0.0.0.0'
PORT = '1000'
DUMMY_URL = 'http://0.0.0.0:1000'
DUMMY_FOLDER = 'dummy_folder'
DUMMY_FILE = 'dummy'
pico_params_dict = {'delay': 10, 'duration': 10, 'voltage_range': 1}
pico_params_dataclass = picoscope.PicoParams(10, 10, 1)


def test_auto_enum():
    """We want the the auto method to be zero-based
    (as opposed to enum's default 1-based).
    """

    status_val = Status.not_started.value

    assert isinstance(status_val, int)
    assert status_val == 0


def test_dataclass_from_dict():
    PicoParams_ = utils.dataclass_from_dict(
        dataclass_=picoscope.PicoParams,
        dict_=pico_params_dict
    )

    assert PicoParams_ == pico_params_dataclass


@pytest.fixture
def created_file():
    os.rmdir(DUMMY_FOLDER)
    dummy_filename = f'{DUMMY_FOLDER}/{DUMMY_FILE}'
    os.mkdir(DUMMY_FOLDER)

    with open(dummy_filename, 'w'):
        pass

    yield

    os.system(f'rm {dummy_filename}')


def test_last_folder_update(created_file):
    timestamp = utils.last_folder_update(folder_path=DUMMY_FOLDER)

    assert isinstance(timestamp, float)
    assert timestamp > 0.0


def test_last_folder_update_no_file_exists():
    timestamp = utils.last_folder_update(folder_path=DUMMY_FOLDER)

    assert isinstance(timestamp, float)
    assert timestamp == -1.0


def test_make_url():
    url = utils.make_url(IP, PORT)

    assert isinstance(url, str)
    assert url == DUMMY_URL
