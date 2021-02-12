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

import yaml

__APP_CONFIG = None


def read_app_config(path=None):
    """
    Read the app config from the config location

    todo: handle the config location and exception

    :return: config dictionary
    :rtype: dict
    """
    global __APP_CONFIG

    if not path:
        path = "conf/config.yaml"

    if not __APP_CONFIG:
        try:
            with open(path) as f:
                __APP_CONFIG = yaml.load(f, Loader=yaml.FullLoader)
        except IOError:
            # raise SystemExit("Unable to load configuration")
            pass
    return __APP_CONFIG


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


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


class CommonConstants(object):

    PARAMS: str = "params"

    HEADERS: str = "headers"

    STOCK_SUMMARY: str = "summary"

    TOKEN: str = "token"

    SYMBOL: str = "symbol"
