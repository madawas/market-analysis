import constants
from constants import DataSources


class Ticker:

    def __init__(self, symbol, exchange, default_datasource=None):
        self.symbol = symbol
        self.exchange = exchange
        self.fallback_order = constants.DEFAULT_DATA_SOURCE_FALLBACK_ORDER

        if default_datasource is None:
            self.datasource = DataSources.IEX_CLOUD
        else:
            self.datasource = default_datasource

    @property
    def datasource(self):
        return self.datasource

    @datasource.setter
    def datasource(self, datasource):
        self.datasource = datasource

    def execute_request(self, data_source):
        pass
