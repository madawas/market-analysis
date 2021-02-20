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

from . import util
from . import datasource as ds
from .exceptions import MarketDataException

log = logging.getLogger(__name__)

DC = util.DataSourceConstants
CC = util.CommonConstants


class Ticker:
    _CONFIG = util.read_app_config()

    def __init__(self, symbol, datasource=None, fallback_datasource=None):
        self.__symbol = symbol

        if not datasource:
            log.warning("datasource parameter is empty. Setting the default datasource specified in the config")
            self.__datasource = Ticker.__create_datasource(Ticker._CONFIG.get(DC.DEFAULT_DATASOURCE))
        else:
            self.__datasource = Ticker.__create_datasource(datasource)

        if not fallback_datasource:
            self.__fallback_datasource = Ticker.__create_datasource(Ticker._CONFIG[DC.DEFAULT_FALLBACK_DATASOURCE])
        else:
            self.__fallback_datasource = Ticker.__create_datasource(fallback_datasource)

    @property
    def datasource(self):
        return self.__datasource

    @datasource.setter
    def datasource(self, datasource):
        self.__datasource = Ticker.__create_datasource(datasource)

    @property
    def fallback_datasource(self):
        return self.__fallback_datasource

    @fallback_datasource.setter
    def fallback_datasource(self, datasource):
        self.__fallback_datasource = Ticker.__create_datasource(datasource)

    @property
    def symbol(self):
        return self.__symbol

    def get_summary(self, datasource: str = None, environment: str = None, token: str = None, version: str = None):
        """
        Get summary of the given ticker symbol

        :param datasource: overrides the data source specified when creating the :Ticker instance. [optional]
        :type datasource: str
        :param environment: overrides the data source/API environment specified when creating the :py:class:Ticker
                instance. [optional]
        :type environment: str
        :param version: overrides the data source/API version specified when creating the Ticker instance. [optional]
        :type version: str
        :param token: overrides the authentication token specified when creating the :py:class:Ticker instance.
                [optional]
        :type token: str
        :return:
        """
        args_dict = {}
        local_ds = self.__datasource if datasource is None else Ticker.__create_datasource(datasource)

        if environment is not None:
            args_dict[DC.API_ENVIRONMENT] = environment

        if version is not None:
            args_dict[DC.API_VERSION] = version

        if token is not None:
            args_dict[CC.TOKEN] = token

        return self.__handle_request(local_ds, CC.STOCK_SUMMARY, **args_dict)

    def __handle_request(self, datasource, function, **kwargs):
        """
        Handles the request to fetch data

        :param datasource: overrides the data source specified when creating the :Ticker instance. [optional]
        :type datasource: :py:class:datasource.DataSource
        :param function: function/endpoint/data to retrieve. E.g. summary, balance_sheet
        :type function: str
        :param kwargs: any other data source related parameters
        :return:
        """
        try:
            response = datasource.call_api(function, self.symbol, **kwargs)
        except requests.exceptions.RequestException as e:
            log.error(f"Error occurred while attempting to fetch data. HTTP Status = {e.response.status_code},"
                      f"Message = {e.response.text}")
            response = self.__handle_fallback_request(function, **kwargs)

        if isinstance(response, requests.models.Response):
            is_fallback, data = Ticker.__is_fallback(datasource, response)
            if is_fallback:
                return self.__handle_fallback_request(function, **kwargs)
            elif isinstance(data, str):
                raise MarketDataException(data)
            elif isinstance(data, dict):
                return data
        else:
            return response

    def __handle_fallback_request(self, function, **kwargs):
        """
        Retries to fetch the data again using the fall back data source

        :param function: function/endpoint/data to retrieve. E.g. summary, balance_sheet
        :type str
        :param kwargs: any other data source related parameters
        :return:
        :raises MarketDataException when error occurred while trying to fetch data through fallback datasource
        """
        try:
            return self.__fallback_datasource.call_api(function, self.symbol, **kwargs)
        except IOError as e:
            raise MarketDataException("Error occurred while fetching data", e)

    @staticmethod
    def __is_fallback(datasource, response):
        """
        Decides whether the response is correct and if not whether should try again using the fallback data source

        :param datasource: current datasource
        :param response: received response
        :return: :bool of whether to try again and data
        """
        if response.status_code is requests.codes.ok:
            return False, response.json()
        else:
            if datasource.is_fallback_code(response):
                log.warning(f"Response returned with status: {response.status_code}, msg: {response.text} and "
                            f"retrying again with fallback data source")
                return True, None
            else:
                msg = f"Error occurred while retrieving data: HTTP Status = {response.status_code}, Message = " \
                      f"{response.text}"
                log.error(msg)
                return False, msg

    @staticmethod
    def __create_datasource(datasource):
        """
        Creates the correct data source instance from the given name

        :param datasource: name of the data source
        :return: instance of :py:class:ds.DataSource
        """
        return ds.create_datasource(datasource)
