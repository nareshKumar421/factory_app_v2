import pyodbc


class HanaConnection:

    def __init__(self, hana_config: dict):
        self.hana = hana_config
        self.schema = hana_config['schema']

    def connect(self):
        return pyodbc.connect(
            f"DRIVER={{HDBODBC}};"
            f"SERVERNODE={self.hana['host']}:{self.hana['port']};"
            f"UID={self.hana['user']};"
            f"PWD={self.hana['password']}"
        )
