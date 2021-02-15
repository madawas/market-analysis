from pathlib import Path

import pytest
import yaml
from marketdata import datasource as ds
from marketdata import util
from marketdata.exceptions import DataSourceException

DC = util.DataSourceConstants


@pytest.fixture
def test_config():
    conf_file_path = Path(__file__).resolve().parent.joinpath("resources", "test_conf.yaml")
    if Path(conf_file_path).exists():
        with open(conf_file_path) as f:
            return yaml.load(f, Loader=yaml.FullLoader)


@pytest.fixture()
def load_app_config():
    conf_file_path = Path(__file__).resolve().parent.joinpath("resources", "test_conf.yaml")
    if Path(conf_file_path).exists():
        util.read_app_config(conf_file_path, True)


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
    with pytest.raises(DataSourceException, match=r".*Configuration object is empty or not a required typ*."):
        ds.DataSource({})


def test_init_invalid_datasource(test_config):
    data_source_list = test_config[DC.DATA_SOURCES_PARENT]
    with pytest.raises(DataSourceException, match=r".*Base Url is required when data source is not a "
                                                  r"library*."):
        ds.DataSource(data_source_list[3])

    with pytest.raises(DataSourceException, match=r".*API Authentication token is a required field and is "
                                                  r"missing in configuration*."):
        ds.DataSource(data_source_list[4])


@pytest.mark.usefixtures("load_app_config")
def test_create_datasource():
    datasource = ds.create_datasource("SampleDataSource1")
    assert isinstance(datasource, ds.DataSource)
    assert datasource.name == "SampleDataSource1"
