import os
import logging
import requests
from requests import HTTPError

from util.exceptions import DataSourceException
from util.constants import DataSourceConstants

logger = logging.getLogger(__name__)


class DataSource(object):
    """
    Abstract datasource class for retrieving market data using data providers.

    :param config a dictionary containing configuration values
    :type config: dict
    :raises DataSourceException if token is not provided for an authenticated data source
    :rtype DataSourceException
    """
    def __init__(self, config):
        try:
            DataSource.__validate_config(config)
        except (TypeError, ValueError) as e:
            raise DataSourceException("Error occurred while validating the configuration to initialize the data source",
                                      e)
        else:
            self.__name = config[DataSourceConstants.NAME]
            self.__auth_token = config[DataSourceConstants.AUTH_TOKEN]
            self.__base_url = config[DataSourceConstants.API_BASE_URL]
            self.__config = config

    def _prepare_url(self, resource):
        return "{}{}".format(self.__base_url, resource)

    def get_data(self, resource, params=None, headers=None):
        """
        Execute HTTP GET request for the given resource and fetch data

        :param resource: resource path
        :param params: query parameters to append to the request
        :param headers: HTTP headers to include to the request
        :return: response data from the request
        :rtype dict
        """

        if params is None:
            params = {}
        params["token"] = self.__auth_token
        url = self._prepare_url(resource)
        response = requests.get(url=url, params=params, headers=headers)
        logger.debug("REQUEST: {}".format(response.request.url))
        logger.debug("RESPONSE: {}".format(response.status_code))
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            raise HTTPError("HTTP error occurred with status = {}, message = {}".format(response.status_code,
                                                                                        response.text))

    @staticmethod
    def __validate_config(config):
        """
        Validating the configuration passed to initialize the data source

        :param config: configuration dictionary
        """
        if not config or not isinstance(config, dict):
            raise TypeError("Configuration object is empty or not a required type")

        # Base URL is required when the data source is not a library
        if not config.get(DataSourceConstants.IS_LIBRARY) and not config.get(DataSourceConstants.API_BASE_URL):
            raise TypeError("Base Url is required when data source is not a library")

        if not config.get(DataSourceConstants.TOKEN_ENV):
            config[DataSourceConstants.TOKEN_ENV] = DataSourceConstants.DEFAULT_TOKEN_ENV

        # Set authentication token from environment variable if auth token is not included in the config
        if config.get(DataSourceConstants.IS_AUTHENTICATED) and not (
                config.get(DataSourceConstants.AUTH_TOKEN) and
                isinstance(config.get(DataSourceConstants.AUTH_TOKEN), str)):
            config[DataSourceConstants.AUTH_TOKEN] = os.getenv(DataSourceConstants.TOKEN_ENV)

        if config[DataSourceConstants.AUTH_TOKEN] is None:
            raise ValueError("API Authentication token is empty")

        if not config.get(DataSourceConstants.RETRY_COUNT):
            config[DataSourceConstants.RETRY_COUNT] = 3

        if not config.get(DataSourceConstants.RETRY_DELAY):
            config[DataSourceConstants.RETRY_DELAY] = 0.5
