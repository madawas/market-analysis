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

from marketdata.util import DataSourceConstants
from marketdata.exceptions import DataSourceException

logger = logging.getLogger(__name__)


class DataSource(object):
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
            self.__name = config.get(DataSourceConstants.NAME)
            self._auth_token = config.get(DataSourceConstants.AUTH_TOKEN)
            self._base_url = config.get(DataSourceConstants.API_BASE_URL)
            self._config = config

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    def _prepare_url(self, resource, **kwargs):
        return "{}{}".format(self._base_url, resource)

    def call_api(self, resource, params=None, headers=None):
        """
        Execute HTTP GET request for the given resource and fetch data

        :param resource: resource path
        :param params: query parameters to append to the request
        :param headers: HTTP headers to include to the request
        :return: response data from the request
        :rtype request.response
        """
        url = self._prepare_url(resource)
        return requests.get(url=url, params=params, headers=headers)

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
        if not config.get(DataSourceConstants.IS_LIBRARY) and not config.get(DataSourceConstants.API_BASE_URL):
            raise TypeError("Base Url is required when data source is not a library")

        if not config.get(DataSourceConstants.TOKEN_ENV_VARIABLE):
            config[DataSourceConstants.TOKEN_ENV_VARIABLE] = DataSourceConstants.DEFAULT_TOKEN_ENV

        # Set authentication token from environment variable if auth token is not included in the config
        if config.get(DataSourceConstants.IS_AUTHENTICATED) and not (
                config.get(DataSourceConstants.AUTH_TOKEN) and
                isinstance(config.get(DataSourceConstants.AUTH_TOKEN), str)):
            raise ValueError("API Authentication token is a required field and is missing in configuration")


class IEXCloud(DataSource):

    __IEX_ENVIRONMENTS = ("sandbox", "production")

    __IEX_VALID_VERSIONS = (
        "stable",
        "latest",
        "v1"
    )

    def __init__(self, config: dict):
        super().__init__(config)
        self.__version = config.get(DataSourceConstants.API_VERSION)
        self.__default_env = config[DataSourceConstants.API_ENVIRONMENT]

    def _validate_config(self, config):
        """
        Validates the config related to IEX cloud data source

        :param config: IEX Cloud configuration
        :raises ValueError when invalid value contains in a config parameter
        :raises TypeError when value is present with an incorrect type
        """
        if not config or not isinstance(config, dict):
            raise TypeError("Configuration object is empty or not a required type")

        if not config.get(DataSourceConstants.API_BASE_URL) and isinstance(config.get(
                DataSourceConstants.API_BASE_URL), dict):
            raise TypeError("IEX Cloud API base url is required and should be a dict")

        if not config.get(DataSourceConstants.AUTH_TOKEN):
            raise ValueError("Authentication token is required to connect with IEX Cloud API")

        if not config.get(DataSourceConstants.API_ENVIRONMENT) or config.get(DataSourceConstants.API_ENVIRONMENT) not\
                in IEXCloud.__IEX_ENVIRONMENTS:
            logger.warning("Provided environment {} is invalid. Default environment {} will be used".format(
                config.get(DataSourceConstants.API_ENVIRONMENT), IEXCloud.__IEX_ENVIRONMENTS[0]))
            config[DataSourceConstants.API_ENVIRONMENT] = IEXCloud.__IEX_ENVIRONMENTS[0]

        if not config.get(DataSourceConstants.API_VERSION):
            config[DataSourceConstants.API_VERSION] = IEXCloud.__IEX_VALID_VERSIONS[0]

    def _prepare_url(self, resource, **kwargs):
        env = kwargs.get(DataSourceConstants.API_ENVIRONMENT, self.__default_env)
        version = kwargs.get(DataSourceConstants.API_VERSION, self.__version)
        return "{}/{}{}".format(self._base_url[env], version, resource)

    def call_api(self, resource, params=None, headers=None):
        if params is None:
            params = {}
        params["token"] = self._auth_token
        return super().call_api(resource, params, headers)


class AlphaVantage(DataSource):
    def __init__(self, config):
        super().__init__(config)

    def _prepare_url(self, resource, **kwargs):
        return super()._prepare_url(resource)

    def call_api(self, resource, params=None, headers=None):
        if params is None or not (params.get("function") and params.get("symbol")):
            raise ValueError("Parameters: function and symbol is required")
        params["apikey"] = self._auth_token
        return super().call_api("", params, headers)
