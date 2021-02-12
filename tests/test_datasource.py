import os

import pytest
import yaml
from marketdata import datasource as ds
from marketdata import util

DC = util.DataSourceConstants


@pytest.fixture
def test_config():
    conf_file_path = os.path.join(os.path.dirname(__file__), "resources/test_conf.yaml")
    if os.path.exists(conf_file_path):
        with open(conf_file_path) as f:
            return yaml.load(f, Loader=yaml.FullLoader)


@pytest.fixture()
def load_app_config():
    conf_file_path = os.path.join(os.path.dirname(__file__), "resources/test_conf.yaml")
    if os.path.exists(conf_file_path):
        util.read_app_config(conf_file_path)


def test_init_generic_datasource(test_config):
    data_source_list = test_config[DC.DATA_SOURCES_PARENT]
    datasource = ds.DataSource(data_source_list[0])
    assert datasource.name == data_source_list[0][DC.NAME]
    ##todo: Think about singleton pattern
    datasource = ds.DataSource(data_source_list[1])
    assert datasource.name == data_source_list[1][DC.NAME]

    datasource = ds.DataSource(data_source_list[2])
    assert datasource.name == data_source_list[2][DC.NAME]


def test_init_invalid_datasource(test_config):
    data_source_list = test_config[DC.DATA_SOURCES_PARENT]
    datasource = ds.DataSource(data_source_list[3])
    assert datasource.name == data_source_list[3][DC.NAME]


@pytest.mark.usefixtures("load_app_config")
def test_create_datasource():
    datasource = ds.create_datasource("GenericDataSource")
    assert isinstance(datasource, ds.DataSource)
    assert datasource.name == "GenericDatasource"
