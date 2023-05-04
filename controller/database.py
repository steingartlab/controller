import sqlite3

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
    """Writes to a local database synced with drops using syncthing.

    Example:
        db_filename = 'test'
        db = database.Database(db_filename)
        while *data is being updated*:
            db.write(payload, table)
    """

    def __init__(self, db_filename: str):
        """
        Args:

        """

        self.connection = sqlite3.connect(f'{PATH}/{db_filename}.sqlite3')
        self.cursor = self.connection.cursor()
        self.cursor.execute(TABLE_INITIALIZER)

    @staticmethod
    def parse_query(payload: dict, table: str = 'acoustics') -> str:
        """Prepares the query."""
        keys: str = ', '.join([key for key in payload.keys()])
        # Very hacky, but leaving for now.
        # We have to parse the amps to a SQL-readable format.
        # It doesn't accept the pythonic list directly—we must parse it to a string literal.
        values_parsed: list = [f'"{str(val)}"' if isinstance(val, list) else str(val) for val in payload.values()]
        values: str = ', '.join(values_parsed)
        
        return f'INSERT INTO {table} ({keys}) VALUES ({values});'


    def write(self, query: str) -> int:
        """Writes data out to Drops.

        Args:
            query (str): The query, see parse_query()

        Returns:
            int: The row ID.
        """
        
        self.cursor.execute(query)
        self.connection.commit()

        return self.cursor.lastrowid
        