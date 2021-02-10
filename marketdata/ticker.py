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

    def __init__(self, symbol, datasource, fallback_datasource=None):
        self.__symbol = symbol

        if not datasource:
            log.warning("datasource parameter is empty. Setting the default datasource specified in the config")
            self.__datasource = Ticker.__create_datasource(Ticker._CONFIG.get(DC.DEFAULT_DATASOURCE))
        else:
            self.__datasource = Ticker.__create_datasource(datasource)

        if not fallback_datasource:
            self.__fallback_datasource = Ticker.__create_datasource(Ticker._CONFIG[DC.DEFAULT_FALLBACK_DATASOURCE])

    @property
    def datasource(self):
        return self.__datasource

    @datasource.setter
    def datasource(self, datasource):
        self.__datasource = Ticker.__create_datasource(datasource)

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
        try:
            response = datasource.call_api(function, self.symbol, **kwargs)
        except requests.exceptions.RequestException as e:
            log.error("Error occurred while attempting to fetch data. HTTP Status = {}, Message = {}".format(
                e.response.status_code, e.response.text))
            response = self.__handle_fallback_request(function, **kwargs)

        if isinstance(response, requests.models.Response):
            is_fallback, data = Ticker.__is_fallback(datasource, response)
            if is_fallback:
                data = self.__handle_fallback_request(function, **kwargs)
            elif isinstance(data, str):
                raise MarketDataException(data)
            elif isinstance(data, dict):
                return data

    def __handle_fallback_request(self, function, **kwargs):
        datasource = Ticker.__create_datasource(self.__fallback_datasource)
        try:
            return datasource.call_api(function, self.symbol, **kwargs)
        except IOError as e:
            raise MarketDataException("Error occurred while fetching data", e)

    @staticmethod
    def __is_fallback(datasource, response):
        if response.status_code is requests.codes.ok:
            return False, response.json()
        else:
            if datasource.is_fallback_code(response):
                log.warning("Response returned with status: {}, msg: {} and retrying again with fallback data source"
                            .format(response.status_code, response.text))
                return True, None
            else:
                msg = "Error occurred while retrieving data: HTTP Status = {}, Message = {}".format(
                    response.status_code, response.text)
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
