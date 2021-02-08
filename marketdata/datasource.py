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

import logging
import requests

from yahoo_fin import stock_info as yf

from . import util
from .exceptions import DataSourceException

DC = util.DataSourceConstants
CC = util.CommonConstants

logger = logging.getLogger(__name__)

__DATA_SOURCES = util.read_app_config()[DC.DATA_SOURCES_PARENT]


def create_datasource(name):
    """
    Create data source instance of the given data source name.

    The function attempts to find the data source config from the config file and creates an instance
    by passing the config to create the instance

    :param name: data source name
    :return: data source instance
    :type: DataSource
    """
    config = next(filter(lambda x: x['name'] == name, __DATA_SOURCES), None)

    if not config:
        return ValueError("Unable to find a configuration to a datasource with name: {}".format(name))

    if not globals()[name]:
        return DataSource(config)
    else:
        return globals()[name](config)


class DataSource(object, metaclass=util.Singleton):
    """
    Abstract datasource class for retrieving market data using data providers.

    :param config a dictionary containing configuration values
    :type config: dict
    :raises DataSourceException if token is not provided for an authenticated data source
    :rtype DataSourceException
    """
    def __init__(self, config: dict):
        try:
            self._validate_config(config)
        except (TypeError, ValueError) as e:
            raise DataSourceException("Error occurred while validating the configuration to initialize the data source",
                                      e)
        else:
            self.__name = config.get(DC.NAME)
            self._auth_token = config.get(DC.AUTH_TOKEN)
            self._base_url = config.get(DC.API_BASE_URL)
            self._resource_mapping = config.get(DC.RESOURCES_MAPPING)
            self._config = config

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    def _prepare_url(self, resource, **kwargs):
        return "{}{}".format(self._base_url, resource)

    def _call_api(self, resource, params=None, headers=None, **kwargs):
        """
        Execute HTTP GET request for the given resource and fetch data

        :param resource: resource path
        :param params: query parameters to append to the request
        :param headers: HTTP headers to include to the request
        :return: response data from the request
        :rtype request.response
        """
        url = self._prepare_url(resource, **kwargs)
        return requests.get(url=url, params=params, headers=headers)

    def call_api(self, function, symbol, **kwargs):
        pass

    def _validate_config(self, config):
        """
        Validates the configuration passed to initialize the data source

        :param config: configuration dictionary
        :raises ValueError when invalid value contains in a config parameter
        :raises TypeError when value is present with an incorrect type
        """
        if not config or not isinstance(config, dict):
            raise TypeError("Configuration object is empty or not a required type")

        # Base URL is required when the data source is not a library
        if not config.get(DC.IS_LIBRARY) and not config.get(DC.API_BASE_URL):
            raise TypeError("Base Url is required when data source is not a library")

        # Set authentication token from environment variable if auth token is not included in the config
        if config.get(DC.IS_AUTHENTICATED) and not (
                config.get(DC.AUTH_TOKEN) and
                isinstance(config.get(DC.AUTH_TOKEN), str)):
            raise ValueError("API Authentication token is a required field and is missing in configuration")


class IEXCloud(DataSource, metaclass=util.Singleton):

    __IEX_ENVIRONMENTS = ("sandbox", "production")

    __IEX_VALID_VERSIONS = (
        "stable",
        "latest",
        "v1"
    )

    def __init__(self, config: dict):
        if not config:
            config = util.read_app_config()
        super().__init__(config)
        self.__version = config.get(DC.API_VERSION)
        self.__default_env = config[DC.API_ENVIRONMENT]

    def _validate_config(self, config):
        """
        Validates the config related to IEX cloud data source

        :param config: IEX Cloud configuration
        :raises ValueError when invalid value contains in a config parameter
        :raises TypeError when value is present with an incorrect type
        """
        if not config or not isinstance(config, dict):
            raise TypeError("Configuration object is empty or not a required type")

        if not config.get(DC.API_BASE_URL) and isinstance(config.get(
                DC.API_BASE_URL), dict):
            raise TypeError("IEX Cloud API base url is required and should be a dict")

        if not config.get(DC.AUTH_TOKEN):
            raise ValueError("Authentication token is required to connect with IEX Cloud API")

        if not config.get(DC.API_ENVIRONMENT) or config.get(DC.API_ENVIRONMENT) not\
                in IEXCloud.__IEX_ENVIRONMENTS:
            logger.warning("Provided environment {} is invalid. Default environment {} will be used".format(
                config.get(DC.API_ENVIRONMENT), IEXCloud.__IEX_ENVIRONMENTS[0]))
            config[DC.API_ENVIRONMENT] = IEXCloud.__IEX_ENVIRONMENTS[0]

        if not config.get(DC.API_VERSION):
            config[DC.API_VERSION] = IEXCloud.__IEX_VALID_VERSIONS[0]

    def _prepare_url(self, resource, **kwargs):
        env = kwargs.get(DC.API_ENVIRONMENT, self.__default_env)
        version = kwargs.get(DC.API_VERSION, self.__version)
        return "{}/{}{}".format(self._base_url[env], version, resource)

    def call_api(self, function, symbol, **kwargs):
        if function is None or symbol is None:
            return ValueError("Symbol and Function are required parameters")
        else:
            params = kwargs.get(CC.PARAMS, None)
            headers = kwargs.get(CC.HEADERS, None)
            token = kwargs.get(CC.TOKEN, None)
            env = kwargs.get(DC.API_ENVIRONMENT, self.__default_env)

            params = {} if params is None else params

            if token is not None:
                params[CC.TOKEN] = token
            else:
                params[CC.TOKEN] = self._auth_token[env]

            resource = self._resource_mapping[function].format(symbol)
            return self._call_api(resource, params, headers, **kwargs)


class AlphaVantage(DataSource, metaclass=util.Singleton):

    __apikey: str = "apikey"
    __function: str = "function"

    def __init__(self, config):
        super().__init__(config)

    def _prepare_url(self, resource, **kwargs):
        return super()._prepare_url(resource, **kwargs)

    def call_api(self, function, symbol, **kwargs):
        if function is None or symbol is None:
            return ValueError("Symbol and Function are required parameters")
        else:
            params = kwargs.get(CC.PARAMS, None)
            token = kwargs.get(AlphaVantage.__apikey)

            params = {} if not params else params

            params[AlphaVantage.__function] = self._resource_mapping[function],
            params[CC.SYMBOL] = symbol

            if token is not None:
                params[AlphaVantage.__apikey] = token
            else:
                params[AlphaVantage.__apikey] = self._auth_token

            return self._call_api("", params, kwargs.get(CC.HEADERS, None), **kwargs)


class YahooFinance(DataSource):

    def __init__(self, config):
        super().__init__(config)

    def _call_api(self, resource, params=None, headers=None, **kwargs):
        function = self._resource_mapping[resource]
        return getattr(yf, function)(params[CC.SYMBOL])

    def call_api(self, function, symbol, **kwargs):
        if function is None or symbol is None:
            return ValueError("Symbol and Function are required parameters")
        else:
            return self._call_api(function, params={CC.SYMBOL: symbol}, headers=None, **kwargs)
