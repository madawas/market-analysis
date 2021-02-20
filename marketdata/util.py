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
from collections import OrderedDict

import yaml

__APP_CONFIG = None


def read_app_config(path: str = None, override_config: bool = True):
    """
    Read the app config from the config location

    :param path: absolute path or relative path from current working directory to the config file
    :param override_config: whether to override the global app config
    :return: config dictionary
    :rtype: dict
    """
    global __APP_CONFIG

    if not override_config and __APP_CONFIG is not None:
        return __APP_CONFIG

    if not (path and Path(path).exists()):
        path = Path(__file__).resolve().parent.parent.joinpath('conf', 'config.yaml').resolve()

    with open(path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if override_config:
        __APP_CONFIG = config

    return config


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LRUCache(object):
    def __init__(self, capacity: int):
        self.__cache = OrderedDict()
        self.__capacity = capacity

    @property
    def capacity(self):
        return self.__capacity

    @capacity.setter
    def capacity(self, capacity: int):
        self.__capacity = capacity

    def get(self, key):
        if key not in self.__cache:
            return None
        else:
            self.__cache.move_to_end(key)
            return self.__cache[key]

    def put(self, key, value):
        self.__cache[key] = value
        self.__cache.move_to_end(key)
        if len(self.__cache) > self.capacity:
            self.__cache.popitem(last=False)


class DataSourceConstants(object):

    DATA_SOURCES_PARENT: str = "datasources"

    RESOURCES_MAPPING: str = "resourceMapping"

    NAME: str = "name"

    IS_LIBRARY: str = "isLibrary"

    IS_AUTHENTICATED: str = "isAuthenticated"

    API_BASE_URL: str = "baseUrl"

    API_VERSION: str = "version"

    API_ENVIRONMENT: str = "environment"

    AUTH_TOKEN: str = "authToken"

    DEFAULT_DATASOURCE: str = "defaultDataSource"

    DEFAULT_FALLBACK_DATASOURCE: str = "defaultFallbackDatasource"

    HTTP_FALLBACK_CODE_LIST: str = "httpFallbackCodes"

    ENV_VARIABLE_PREFIX: str = "env."


class CommonConstants(object):

    PARAMS: str = "params"

    HEADERS: str = "headers"

    STOCK_SUMMARY: str = "summary"

    TOKEN: str = "token"

    SYMBOL: str = "symbol"
