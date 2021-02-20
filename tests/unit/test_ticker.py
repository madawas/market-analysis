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
from pathlib import Path
from unittest.mock import patch, PropertyMock, Mock

import pytest
import yaml

from marketdata import datasource as ds
from marketdata.ticker import Ticker

sample_response = {
    "symbol": "SMBL",
    "companyName": "Sample Company",
    "marketcap": 2250499705006,
    "week52high": 146.83,
    "week52low": 54.2,
    "week52highSplitAdjustOnly": 149.48,
    "week52lowSplitAdjustOnly": 53.22,
    "week52change": 0.6922728897981629,
    "sharesOutstanding": 17482855789,
    "float": 0,
    "avg10Volume": 81826592,
    "avg30Volume": 99428456,
    "day200MovingAvg": 122.74,
    "day50MovingAvg": 137.43,
    "employees": 148717,
    "ttmEPS": 3.8,
}


@pytest.fixture
def test_config():
    """
    Reads test app config
    """
    conf_file_path = Path(__file__).resolve().parent.parent.joinpath("resources", "test_conf.yaml")
    if Path(conf_file_path).exists():
        with open(conf_file_path) as f:
            return yaml.load(f, Loader=yaml.FullLoader)


@pytest.fixture
def mock_ds_app_config(mocker, test_config):
    """
    Mocks the app configuration from datasource module
    """
    yield mocker.patch("marketdata.datasource.util.read_app_config", return_value=test_config, autospec=True)


@patch.object(Ticker, "_CONFIG", new_callable=PropertyMock)
@patch("marketdata.datasource.create_datasource", autospec=True)
def test_ticker_initialization(mock_create_ds, mock_config, test_config):
    mock_config.return_value = test_config
    mocks = [Mock(), Mock(), Mock(), Mock()]
    mocks[0].name = "Sample Data Source"
    mocks[1].name = "Sample Fallback Datasource"
    mocks[2].name = "DefaultDataSource"
    mocks[3].name = "DefaultFallbackDataSource"
    mock_create_ds.side_effect = mocks

    ticker = Ticker("SMBL", datasource="SampleDS", fallback_datasource="SampleFbDs")
    assert mock_create_ds.call_count == 2, "The function should be called twice to create primary data source and " \
                                           "the fallback data source"
    assert ticker.datasource.name == mocks[0].name
    assert ticker.fallback_datasource.name == mocks[1].name

    ticker = Ticker("SM2")
    assert ticker.datasource.name == mocks[2].name
    assert ticker.fallback_datasource.name == mocks[3].name
    assert mock_create_ds.call_count == 4


@patch.object(Ticker, "_CONFIG", new_callable=PropertyMock)
@pytest.mark.usefixtures("mock_ds_app_config")
def test_create_ticker(mock_config, test_config):
    """
    Tests creating :py:class:Ticker instance
    """
    mock_config.return_value = test_config
    tkr = Ticker(symbol="SMBL", datasource="SampleDataSource2")

    assert tkr.symbol == "SMBL"
    assert isinstance(tkr.datasource, ds.DataSource)
    assert tkr.datasource.name == "SampleDataSource2"
    assert isinstance(tkr.fallback_datasource, ds.YahooFinance)
    assert tkr.fallback_datasource.name == "YahooFinance"


@patch.object(Ticker, "_CONFIG", new_callable=PropertyMock)
@pytest.mark.usefixtures("mock_ds_app_config")
def test_ticker_properties(mock_config, test_config):
    mock_config.return_value = test_config
    tkr = Ticker(symbol="SMBL", datasource="SampleDataSource2")
    assert tkr.datasource.name == "SampleDataSource2"
    tkr.datasource = "SampleDataSource1"
    assert tkr.datasource.name == "SampleDataSource1"
    assert isinstance(tkr.fallback_datasource, ds.YahooFinance)

    tkr2 = Ticker(symbol="XMPL")
    assert tkr2.datasource.name == "SampleDataSource1"
    tkr2.fallback_datasource = "SampleDataSource3"
    assert isinstance(tkr2.fallback_datasource, ds.DataSource)


@patch.object(Ticker, "_CONFIG", new_callable=PropertyMock)
@patch("marketdata.datasource.create_datasource", return_value=Mock(), autospec=True)
def test_ticker_summary_success(mock_create_ds, mock_config, test_config):
    mock_config.return_value = test_config
    response = Mock()
    response.status_code = 200
    response.json.return_value = sample_response

    datasource = mock_create_ds.return_value
    datasource.call_api.return_value = response

    ticker = Ticker("SMBL", datasource="Sample Datasource")
    summary = ticker.get_summary()
    assert summary.status_code == 200, "Response code should be successful"
    assert summary.json() == sample_response
