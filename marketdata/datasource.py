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

import os
import logging
import requests

from yahoo_fin import stock_info as yf

from . import util
from .exceptions import DataSourceException

DC = util.DataSourceConstants
CC = util.CommonConstants

log = logging.getLogger(__name__)


def create_datasource(name):
    """
    Create data source instance of the given data source name.

    The function attempts to find the data source config from the config file and creates an instance
    by passing the config to create the instance

    :param name: data source name
    :return: data source instance
    :type: DataSource
    """
    config = util.read_app_config(override_config=False)
    if isinstance(config, dict):
        datasource_list = config[DC.DATA_SOURCES_PARENT]
    else:
        raise TypeError("config is not a dict")
    config = next(filter(lambda x: x['name'] == name, datasource_list), None)

    if not config:
        return ValueError(f"Unable to find a configuration to a datasource with name: {name}")

    try:
        # Check if a class from the given name exists and create an object from that
        return globals()[name](config)
    except KeyError:
        return DataSource(config)


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
            raise DataSourceException(f"Configuration validation failed with error: [{e}]")
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
        """
        Combines the base url and resource to generate the complete URI of the resource to access

        :param resource: resource to access
        :param kwargs: additional parameters
        :return: url to call
        """
        return f"{self._base_url}/{resource}"

    def _call_api(self, resource, params=None, headers=None, **kwargs):
        """
        Executes HTTP GET request for the given resource and fetch data

        :param resource: resource path
        :param params: query parameters to append to the request
        :param headers: HTTP headers to include to the request
        :return: response data from the request
        """
        url = self._prepare_url(resource, **kwargs)
        return requests.get(url=url, params=params, headers=headers)

    def call_api(self, function, symbol, **kwargs):
        """
        Invokes the backend API to retrieve data

        :param function: function/resource to invoke
        :param symbol: ticker/symbol
        :param kwargs: additional parameters to pass to the backend
        :return: response data from the requesr
        """
        resource = self._resource_mapping[function].format(symbol)
        return self._call_api(resource, kwargs.get(CC.PARAMS, None), kwargs.get(CC.HEADERS, None), **kwargs)

    def is_fallback_code(self, response):
        """
        Checks the HTTP error code against the list of fallback codes specified in the documentation

        :param response: HTTP response
        :return: true if the error code exists in the fallback code list
        """
        if response.status_code in self._config[DC.HTTP_FALLBACK_CODE_LIST]:
            return True
        else:
            return False

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

        if config.get(DC.IS_AUTHENTICATED):
            tok = config.get(DC.AUTH_TOKEN)
            if not (tok and isinstance(tok, str)):
                raise ValueError("API Authentication token is a required field and is missing in configuration")
            elif config.get(DC.AUTH_TOKEN).startswith(DC.ENV_VARIABLE_PREFIX):
                tok = os.environ.get(tok[len(DC.ENV_VARIABLE_PREFIX):])
                if not (tok and isinstance(tok, str)):
                    raise ValueError(f"Auth token cannot be found in {tok[len(DC.ENV_VARIABLE_PREFIX):]} "
                                     f"environment variable")
                else:
                    config[DC.AUTH_TOKEN] = tok


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
        :raises ValueError when incorrect value is present
        """
        if not config or not isinstance(config, dict):
            raise TypeError("Configuration object is empty or not a required type")

        if not config.get(DC.API_BASE_URL) and isinstance(config.get(
                DC.API_BASE_URL), dict):
            raise TypeError("IEX Cloud API base url is required and should be a dict")

        auth_token = config.get(DC.AUTH_TOKEN)
        if not auth_token or not isinstance(auth_token, dict):
            raise ValueError("Authentication token is required to connect with IEX Cloud API")
        else:
            for env in IEXCloud.__IEX_ENVIRONMENTS:
                tok = auth_token[env]
                if tok is not None and tok.startswith(DC.ENV_VARIABLE_PREFIX):
                    tok = os.environ.get(tok[len(DC.ENV_VARIABLE_PREFIX):])
                    if not tok:
                        log.warning(f"Auth token for {env} is not provided.")
                        del auth_token[env]
                    else:
                        # todo: validate starts from auth token
                        auth_token[env] = tok

        if not config.get(DC.API_ENVIRONMENT) or config.get(DC.API_ENVIRONMENT) not \
                in IEXCloud.__IEX_ENVIRONMENTS:
            log.warning(f"Provided environment {DC.API_ENVIRONMENT} is invalid. Default environment "
                        f"{IEXCloud.__IEX_ENVIRONMENTS[0]} will be used")
            config[DC.API_ENVIRONMENT] = IEXCloud.__IEX_ENVIRONMENTS[0]

        if not config.get(DC.API_VERSION):
            config[DC.API_VERSION] = IEXCloud.__IEX_VALID_VERSIONS[0]

    def _prepare_url(self, resource, **kwargs):
        env = kwargs.get(DC.API_ENVIRONMENT, self.__default_env)
        version = kwargs.get(DC.API_VERSION, self.__version)
        return f"{self._base_url[env]}/{version}{resource}"

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
