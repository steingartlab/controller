import os
import sqlite3

import pytest

from controller import database

DB_FILENAME = 'test'
FOLDER = 'acoustics'
dummy_query = 'INSERT INTO acoustics (time, amps) VALUES (0, "[0.1, 0.2]");'
dummy_waveform = [0.1, 0.2]
dummy_data = {'time': 0.0, 'amps': dummy_waveform}
dummy_payload = {'amps': dummy_waveform}


def find_table(filename) -> str:
    """Helper function for finding table names in database."""

    connection = sqlite3.connect(f'{FOLDER}/{filename}.sqlite3')
    cursor = connection.cursor()
    query = """SELECT name FROM sqlite_master"""# WHERE type='table'"""
    cursor.execute(query)
    table = cursor.fetchall()
    connection.close()

    return table[0][0]


@pytest.fixture
def teardown():
    yield 

    os.remove(f'{FOLDER}/{DB_FILENAME}.sqlite3')


def test_create_table(teardown):
    database.Database(DB_FILENAME)

    table = find_table(DB_FILENAME)

    assert table == 'acoustics'


@pytest.fixture
def instance(teardown):
    instance = database.Database(DB_FILENAME)

    return instance


def test_parse_query(instance):
    query = instance.parse_query(dummy_data)

    assert isinstance(query, str)


def test_write(instance):
    row_id = instance.write(query=dummy_query)

    assert row_id == 1

def test_save(instance):
    row_id = database.save(dummy_payload, instance)

    assert row_id == 1
