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


def read_config():
    with open("conf/config.yaml") as conf:
        config = yaml.load(conf, Loader=yaml.FullLoader)
        print(config)
    return config


class DataSourceConstants(object):

    NAME: str = "name"

    IS_LIBRARY: str = "isLibrary"

    IS_AUTHENTICATED: str = "isAuthenticated"

    API_BASE_URL: str = "baseUrl"

    API_VERSION: str = "version"

    API_ENVIRONMENT: str = "environment"

    AUTH_TOKEN: str = "authToken"

    TOKEN_ENV_VARIABLE: str = "authTokenEnv"

    DEFAULT_TOKEN_ENV: str = "DATASOURCE_TOKEN"
