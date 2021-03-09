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
from datetime import datetime, timedelta

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


class LRUCache(object):
    """
    LRU Cache with TTL support
    """
    def __init__(self, capacity: int = 50, ttl: int = 900):
        """
        Initializes a cache object

        :param capacity: cache capacity. default 50
        :param ttl: expiry period. default 900s
        """
        self.__cache = OrderedDict()
        self.__capacity = capacity
        self.__ttl = ttl

    @property
    def capacity(self):
        return self.__capacity

    @capacity.setter
    def capacity(self, capacity: int):
        self.__capacity = capacity

    @property
    def ttl(self):
        return self.__ttl

    @ttl.setter
    def ttl(self, ttl: int):
        self.__ttl = ttl

    def __contains__(self, key):
        if key in self.__cache and self.__cache[key] is not None and self.__cache[key]["expiry"] > datetime.now():
            return True
        return False

    def get(self, key):
        """
        Retrieve item from cache

        :param key: cache key
        :return: item if exists and not expired
        """
        if key in self.__cache:
            self.__cache.move_to_end(key)
            cache_val = self.__cache[key]
            if cache_val["expiry"] < datetime.now():
                del self.__cache[key]
            else:
                return cache_val["value"]
        return None

    def put(self, key, value, ttl: int = -1):
        """
        Puts an item in to cache

        :param key: cache key
        :param value: value
        :param ttl: optional ttl value to override default ttl value
        """
        if ttl != -1:
            ttl = self.__ttl

        expires = datetime.now() + timedelta(seconds=ttl)

        cache_val = {
            "value": value,
            "expiry": expires
        }
        self.__cache[key] = cache_val
        self.__cache.move_to_end(key)

        if len(self.__cache) > self.capacity:
            self.__cache.popitem(last=False)


class DataSourceConstants(object):

    DATA_SOURCES_PARENT: str = "datasources"

    RESOURCES_MAPPING: str = "resourceMapping"

    NAME: str = "name"

    TYPE: str = "type"

    IS_LIBRARY: str = "isLibrary"

    IS_AUTHENTICATED: str = "isAuthenticated"

    API_BASE_URL: str = "baseUrl"

    DATASOURCE: str = "datasource"

    API_VERSION: str = "version"

    API_ENVIRONMENT: str = "environment"

    AUTH_TOKEN: str = "authToken"

    DEFAULT_DATASOURCE: str = "defaultDataSource"

    DEFAULT_FALLBACK_DATASOURCE: str = "defaultFallbackDatasource"

    HTTP_FALLBACK_CODE_LIST: str = "httpFallbackCodes"

    ENV_VARIABLE_PREFIX: str = "env."

    CACHE_CAPACITY: str = "cacheCapacity"

    CACHE_EXPIRY: str = "cacheExpiry"


class CommonConstants(object):

    PARAMS: str = "params"

    HEADERS: str = "headers"

    STOCK_SUMMARY: str = "summary"

    SUMMARY_ADVANCED: str = "summary_advanced"

    TOKEN: str = "token"

    SYMBOL: str = "symbol"
