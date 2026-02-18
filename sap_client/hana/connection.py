from hdbcli import dbapi


class HanaConnection:

    def __init__(self, hana_config: dict):
        self.hana = hana_config
        self.schema = hana_config['schema']

    def connect(self):
        return dbapi.connect(
            address=self.hana['host'],
            port=self.hana['port'],
            user=self.hana['user'],
            password=self.hana['password'],
        )
