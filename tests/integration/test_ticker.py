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

import pytest

from marketdata import util, datasource as ds
from marketdata.ticker import Ticker

DC = util.DataSourceConstants


@pytest.fixture
def default_config():
    """
    Loads the default app configuration
    """
    return util.read_app_config(override_config=True)


def test_ticker_init(default_config):
    ticker = Ticker("AAPL")
    assert ticker.symbol == "AAPL"
    assert ticker.datasource.name == default_config.get(DC.DEFAULT_DATASOURCE)
    assert ticker.fallback_datasource.name == default_config.get(DC.DEFAULT_FALLBACK_DATASOURCE)

    ticker = Ticker("NFLX", "AlphaVantage")
    assert ticker.symbol == "NFLX"
    assert isinstance(ticker.datasource, ds.AlphaVantage)
    assert ticker.fallback_datasource.name == default_config.get(DC.DEFAULT_FALLBACK_DATASOURCE)

    ticker = Ticker("FB", "YahooFinance", "IEXCloud")
    assert ticker.symbol == "FB"
    assert isinstance(ticker.datasource, ds.YahooFinance)
    assert isinstance(ticker.fallback_datasource, ds.IEXCloud)


@pytest.mark.usefixtures("default_config")
def test_ticker_summary():
    ticker = Ticker("NFLX")
    summary = ticker.get_summary()

    assert summary is not None
    assert isinstance(summary, dict)
    assert summary["companyName"] is not None and isinstance(summary["companyName"], str)

    ticker.datasource = "AlphaVantage"
    summary = ticker.get_summary()

    assert summary is not None
    assert isinstance(summary, dict)
    assert summary["Name"] is not None and isinstance(summary["Name"], str)


@pytest.mark.usefixtures("default_config")
def test_ticker_fallback():
    ticker = Ticker("CBA.AX")
    summary = ticker.get_summary()
    assert summary is not None
    assert isinstance(summary, dict)
