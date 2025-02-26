"""Create and write to a sqlite database. Our schema is one table per database
because it goes well with out data "lake" (drops: https://github.com/dansteingart/drops).
"""

import json
import sqlite3
from typing import Dict, List, Union

import numpy as np

PATH = 'acoustics'
TABLE = 'acoustics'
TABLE_INITIALIZER= f'''CREATE TABLE IF NOT EXISTS {TABLE} (
    time REAL PRIMARY KEY,
    amps BLOB,
    metadata TEXT
)
'''

Payload = Union[float, int]#, np.ndarray]


class Database:
    """Writes to a local database that is synced with drops using syncthing.

    Attributes:
        self.client: The mqtt-client responsible for starting and
            maintaining the connection.

    Example:
        db = database.Database(machine='brix2', path='INL_GT_DE_2022_08_01_1')
        while *data is being updated*:
            db.write(payload, table)
    """

    query: str = f'INSERT INTO {TABLE} (time, amps) VALUES (?, ?)'
    
    def __init__(self, db_filename: str):
        """
        Args:
            db_filename (str): Generally stick to experiment ID.
        """

        database: str = f'{PATH}/{db_filename}.sqlite3'
        self.connection = sqlite3.connect(database=database)
        self.cursor = self.connection.cursor()
        self.cursor.execute(TABLE_INITIALIZER)

    @staticmethod
    def _parse_parameters(parameters: List[Payload]) -> tuple:
        parsed = list()

        for parameter in parameters:
            if isinstance(parameter, list):
                parsed.append(sqlite3.Binary(np.array(parameter, dtype=np.float16)))
                continue

            parsed.append(parameter)

        return tuple(parsed)
    
    def write_metadata(self, metadata: dict) -> None:
        metadata_json: str = json.dumps(metadata)
        query: str = f'INSERT INTO {TABLE} (metadata) VALUES (?)'
        self.cursor.execute(query, (metadata_json,))
    
    def write(self, payload: Dict[str, Payload]):
        """Writes data out to Drops.


        """

        parameters = self._parse_parameters(parameters=list(payload.values()))
        self.cursor.execute(Database.query, parameters)
        self.connection.commit()

        return self.cursor.lastrowid
