# Copyright (c) 2021, Madawa Soysa
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datasource as ds


class Ticker:

    __DEFAULT_FALLBACK_DATASOURCE = "YahooFinance"

    def __init__(self, symbol, exchange, datasource, fallback_datasource=None):
        self.__symbol = symbol
        self.__exchange = exchange

        if not datasource:
            raise ValueError("Missing required argument: datasource")
        else:
            self.__datasource = ds.create_datasource(datasource)

        if not fallback_datasource:
            self.__fallback_datasource = ds.create_datasource(Ticker.__DEFAULT_FALLBACK_DATASOURCE)

    @property
    def datasource(self):
        return self.datasource

    @datasource.setter
    def datasource(self, datasource):
        self.datasource = datasource

    def get_summary(self):
        pass
