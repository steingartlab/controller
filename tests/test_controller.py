from time import sleep

import pytest

from controller import controller, picoscope

dummy_exp_settings = {'exp_duration_h': '1', 'interval': '10', 'exp_id': 'test'}
dummy_folder = 'dummy_folder'
dummy_pico_params_dict = {'delay': 10, 'duration': 10, 'voltage_range': 0.1}
dummy_pico_params = picoscope.PicoParams(**dummy_pico_params_dict)
dummy_incoming = {'exp_duration_h': '1', 'interval': '10', 'exp_id': 'test', 'delay': 10, 'duration': 10, 'voltage_range': 0.1}


def test_pulse_low_level():
    waveform = controller._pulse(dummy_pico_params)

    assert isinstance(waveform, dict)
    assert isinstance(waveform['amps'], list)
    assert isinstance(waveform['amps'][0], list)
    assert isinstance(waveform['amps'][0][0], float)


def test_pulse_wrapper():
    controller.pulse(incoming=dummy_pico_params_dict)


@pytest.fixture
def exp_settings():
    exp_settings = controller.ExpSettings(**dummy_exp_settings)

    return exp_settings


def test_exp_settings_post_init_typing(exp_settings):

    assert isinstance(exp_settings.exp_duration_h, float)
    assert isinstance(exp_settings.interval, float)


def test_exp_settings_exp_duration_s(exp_settings):
    exp_duration_s = exp_settings.exp_duration_s

    assert isinstance(exp_duration_s, float)
    assert exp_duration_s == 3600


def test_status():
    not_started_value = controller.Status(0).value

    assert not_started_value == 0


@pytest.fixture
def instance():
    instance = controller.Controller()

    return instance


def test_get_controller_status(instance):
    status = instance.status

    assert status == 0


def test_set_controller_status(instance):
    instance.status = 1

    assert instance.status == 1


def test_controller_last_updated(instance):
    last_updated = instance.last_updated

    assert last_updated > 0  # This breaks if the acoustics folder doesn't exist


def test_controller_time_elapsed_not_started(instance):
    time_elapsed = instance.time_elapsed

    assert time_elapsed is None


@pytest.fixture
def started(instance):
    controller.start_thread(
        controller_=instance,
        incoming=dummy_incoming
    )
    sleep(2)
    yield instance

    instance.stop()


def test_controller_time_elapsed(started):
    time_elapsed = started.time_elapsed

    assert time_elapsed > 0
    

# def test_controller_loop_start():


def test_controller_stop(instance):
    controller.start_thread(
        controller_=instance,
        incoming=dummy_incoming
    )
    sleep(2)
    instance.stop()

    assert instance.status == 2


@pytest.fixture
def finished(instance):
    dummy_incoming_short = {'exp_duration_h': '0.001', 'interval': '10', 'exp_id': 'test', 'delay': 10, 'duration': 10, 'voltage_range': 0.1}
    controller.start_thread(
        controller_=instance,
        incoming=dummy_incoming_short
    )
    sleep(10)

    return instance


# def test_controller_status_updated_after_experiment_finishes(finished):
#     assert finished.status == 2


def test_start_thread(instance):
    controller.start_thread(controller_=instance, incoming=dummy_incoming)
    sleep(2)

    assert instance.status == 1
    
    instance.stop()

