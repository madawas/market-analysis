import os
from pathlib import Path
from unittest import mock

import pytest
import yaml
from marketdata import datasource as ds
from marketdata import util
from marketdata.exceptions import DataSourceException

DC = util.DataSourceConstants


@pytest.fixture
def test_config():
    """
    Read the test configuration and return the configuration

    :return: test configuration
    :rtype: dict
    """
    conf_file_path = Path(__file__).resolve().parent.joinpath("resources", "test_conf.yaml")
    if Path(conf_file_path).exists():
        with open(conf_file_path) as f:
            return yaml.load(f, Loader=yaml.FullLoader)


@pytest.fixture
def load_test_app_config():
    """
    Loads the test app configuration to the library using utility function
    """
    conf_file_path = Path(__file__).resolve().parent.joinpath("resources", "test_conf.yaml")
    if Path(conf_file_path).exists():
        util.read_app_config(conf_file_path, True)


@pytest.fixture
def load_default_config():
    """
    Loads the default app configuration
    """
    util.read_app_config(override_config=True)


def test_init_generic_datasource(test_config):
    """
    Test creating generic data source objects

    :param test_config: config
    """
    data_source_list = test_config[DC.DATA_SOURCES_PARENT]
    datasource = ds.DataSource(data_source_list[0])
    assert datasource.name == data_source_list[0][DC.NAME]
    datasource = ds.DataSource(data_source_list[1])
    assert datasource.name == data_source_list[1][DC.NAME]

    datasource = ds.DataSource(data_source_list[2])
    assert datasource.name == data_source_list[2][DC.NAME]


def test_init_datasource_with_empty_config():
    """
    Tests the behaviour when a data source is created without a config
    """
    with pytest.raises(DataSourceException, match=r".*Configuration object is empty or not a required typ*."):
        ds.DataSource({})


def test_init_invalid_datasource(test_config):
    """
    Tests creating data sources with invalid configurations

    :param test_config: test config
    """
    data_source_list = test_config[DC.DATA_SOURCES_PARENT]
    with pytest.raises(DataSourceException, match=r".*Base Url is required when data source is not a "
                                                  r"library*."):
        ds.DataSource(data_source_list[3])

    with pytest.raises(DataSourceException, match=r".*API Authentication token is a required field and is "
                                                  r"missing in configuration*."):
        ds.DataSource(data_source_list[4])


@pytest.mark.usefixtures("load_test_app_config")
def test_create_datasource():
    """
    Tests creating data sources with the create_datasource function
    """
    datasource = ds.create_datasource("SampleDataSource1")
    assert isinstance(datasource, ds.DataSource)
    assert datasource.name == "SampleDataSource1"


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


# @mock.patch.dict(os.environ, {"IEX_SANDBOX_TOKEN": ""})
# def test_iex_cloud_ds_without_auth_token():
#     with pytest.raises(DataSourceException, match=".*Authentication token is not provided for none of the "
#                                                   "environments*."):
#         ds.create_datasource("IEXCloud")


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
