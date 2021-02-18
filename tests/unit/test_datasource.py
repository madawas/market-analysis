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

import pytest
import yaml

from marketdata import datasource as ds
from marketdata import util
from marketdata.exceptions import DataSourceException

DC = util.DataSourceConstants


@pytest.fixture(autouse=True)
def mock_app_config(mocker):
    """
    Mocks the app configuration
    """
    conf_file_path = Path(__file__).resolve().parent.parent.joinpath("resources", "test_conf.yaml")
    if Path(conf_file_path).exists():
        with open(conf_file_path) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    yield mocker.patch("marketdata.datasource.util.read_app_config", return_value=config, autospec=True)


def test_init_generic_ds():
    """
    Test creating generic data source objects
    """
    test_config = util.read_app_config()
    data_source_list = test_config[DC.DATA_SOURCES_PARENT]
    datasource = ds.DataSource(data_source_list[0])
    assert datasource.name == data_source_list[0][DC.NAME]
    datasource = ds.DataSource(data_source_list[1])
    assert datasource.name == data_source_list[1][DC.NAME]

    datasource = ds.DataSource(data_source_list[2])
    assert datasource.name == data_source_list[2][DC.NAME]


def test_init_invalid_ds():
    """
    Tests creating data sources with invalid configurations
    """
    test_config = util.read_app_config()
    data_source_list = test_config[DC.DATA_SOURCES_PARENT]
    with pytest.raises(DataSourceException, match=r".*Base Url is required when data source is not a "
                                                  r"library*."):
        ds.DataSource(data_source_list[3])

    with pytest.raises(DataSourceException, match=r".*API Authentication token is a required field and is "
                                                  r"missing in configuration*."):
        ds.DataSource(data_source_list[4])


def test_create_generic_ds():
    """
    Tests creating a generic data source using create data source function
    """
    test_config = util.read_app_config()
    data_source_list = test_config[DC.DATA_SOURCES_PARENT]

    datasource = ds.create_datasource(data_source_list[0][DC.NAME])
    assert isinstance(datasource, ds.DataSource)
    assert datasource.name == data_source_list[0][DC.NAME]

    datasource = ds.create_datasource(data_source_list[1][DC.NAME])
    assert isinstance(datasource, ds.DataSource)
    assert datasource.name == data_source_list[1][DC.NAME]

    datasource = ds.create_datasource(data_source_list[2][DC.NAME])
    assert isinstance(datasource, ds.DataSource)
    assert datasource.name == data_source_list[2][DC.NAME]


def test_create_generic_ds_with_invalid_config():
    """
    Tests creating a generic data source with invalid config using create data source function
    """
    test_config = util.read_app_config()
    data_source_list = test_config[DC.DATA_SOURCES_PARENT]

    with pytest.raises(DataSourceException):
        ds.create_datasource(data_source_list[3][DC.NAME])

    with pytest.raises(DataSourceException):
        ds.create_datasource(data_source_list[4][DC.NAME])


def test_create_ds_without_config():
    """
    Test creating a datasource where the data source config does not exist in the app config
    """
    with pytest.raises(ValueError):
        ds.create_datasource("XXX")


def test_init_ds_with_empty_config():
    """
    Tests the behaviour when a data source is created without a config
    """
    with pytest.raises(DataSourceException, match=r".*Configuration object is empty or not a required typ*."):
        ds.DataSource({})


# noinspection PyTypeChecker
def test_init_ds_with_invalid_conf_type():
    """
    Tests creating data source instances with invalid config type
    """
    with pytest.raises(DataSourceException, match=".*Configuration object is empty or not a required type*."):
        ds.DataSource(None)

    with pytest.raises(DataSourceException, match=".*Configuration object is empty or not a required type*."):
        ds.DataSource("config")
