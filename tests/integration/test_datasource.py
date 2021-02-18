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

from marketdata import datasource as ds
from marketdata import util


@pytest.fixture
def load_default_config():
    """
    Loads the default app configuration
    """
    util.read_app_config(override_config=True)


@pytest.mark.usefixtures("load_default_config")
def test_iex_cloud_data_source():
    """
    Tests creating IEXCloud data source using the default config and invoke a basic API call
    """
    iex = ds.create_datasource("IEXCloud")
    assert isinstance(iex, ds.IEXCloud)
    response = iex.call_api("summary", "aapl")
    assert response.status_code == 200, "response code should be 200"
    data = response.json()
    assert isinstance(data, dict)
    assert data["companyName"] == "Apple Inc"


@pytest.mark.usefixtures("load_default_config")
def test_av_data_source():
    """
    Tests creating AlphaVantage data source using the default config and invoke a basic API call
    """
    av = ds.create_datasource("AlphaVantage")
    assert isinstance(av, ds.AlphaVantage)
    response = av.call_api("summary", "aapl")
    assert response.status_code == 200, "response code should be 200"
    data = response.json()
    assert isinstance(data, dict)
    assert response.json()["Name"] == "Apple Inc"


@pytest.mark.usefixtures("load_default_config")
def test_yf_data_source():
    """
    Tests creating YahooFinance data source using the default config and invoke a basic resource
    """
    yf = ds.create_datasource("YahooFinance")
    assert isinstance(yf, ds.YahooFinance)
    response = yf.call_api("summary", "aapl")
    assert isinstance(response, dict)
    assert "1y Target Est" in response
    assert "Ask" in response
