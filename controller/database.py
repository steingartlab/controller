import sqlite3
from time import time

PATH = 'acoustics'
TABLE = 'acoustics'
TABLE_INITIALIZER = f'''CREATE TABLE IF NOT EXISTS {TABLE} (
                            amps BLOB,
                            time REAL PRIMARY KEY,
                            delay REAL,
                            voltage_range REAL,
                            duration REAL
                        )
                     '''


class Database:
    """
    Writes to a local database synced with drops using Syncthing.

    Example:
        db_filename = 'test'
        db = Database(db_filename)
        while *data is being updated*:
            db.write(payload, table)
    """

    def __init__(self, db_filename: str):
        """

        Args:
            db_filename (str): The name of the database file.

        """

        self.connection = sqlite3.connect(f'{PATH}/{db_filename}.sqlite3')
        self.cursor = self.connection.cursor()
        self.cursor.execute(TABLE_INITIALIZER)

    @staticmethod
    def parse_query(payload: dict, table: str = 'acoustics') -> str:
        """Prepares the query for writing data.

        Args:
            payload (dict): The data payload.
            table (str, optional): The table name. Defaults to 'acoustics'.

        Returns:
            str: The prepared SQL query.
        """

        keys: str = ', '.join([key for key in payload.keys()])
        # Very hacky, but leaving for now.
        # We have to parse the amps to a SQL-readable format.
        # It doesn't accept the pythonic list directly—we must parse it to a string literal.
        values_parsed: list = [f'"{str(val)}"' if isinstance(val, list) else str(val) for val in payload.values()]
        values: str = ', '.join(values_parsed)

        return f'''
                INSERT INTO
                    {table} ({keys})
                VALUES
                    ({values});
                '''

    def write(self, query: str) -> int:
        """Writes data to the database.

        Args:
            query (str): The query generated using parse_query().

        Returns:
            int: The row ID of the inserted data.

        """

        self.cursor.execute(query)
        self.connection.commit()

        return self.cursor.lastrowid


def save(waveform: dict[str, list[float]], database_: Database) -> int:
    """Wrapper for saving data to database.
    
    Args:
        waveform: (dict[str, list[float]]): Waveform as received from picoscope.
        database_ (Database): Database instance.

    Returns:
        int: Table row ID.        
    """
    
    timestamp: dict[str, float] = {'time': time()}
    waveform.update(timestamp)
    query: str = Database.parse_query(payload=waveform)

    return Database.write(self=database_, query=query)