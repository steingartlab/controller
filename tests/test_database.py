import os
import sqlite3

import pytest

from controller import database

DB_FILENAME = 'test'
FOLDER = 'acoustics'


@pytest.fixture
def instance():
    yield 

    os.remove(f'{FOLDER}/{DB_FILENAME}.sqlite3')


def find_table(filename) -> str:
    """Also changed this halfway through so am fetching dynamically."""

    connection = sqlite3.connect(f'{FOLDER}/{filename}.sqlite3')
    cursor = connection.cursor()
    query = """SELECT name FROM sqlite_master"""# WHERE type='table'"""
    cursor.execute(query)
    table = cursor.fetchall()
    connection.close()
    print(table)

    return table[0][0]



def test_create_table(instance):
    db = database.Database(DB_FILENAME)

    table = find_table(DB_FILENAME)

    assert table == 'acoustics'



