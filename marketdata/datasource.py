import os
import logging
import requests
from util.exceptions import AuthenticationException

logger = logging.getLogger(__name__)


class DataSource(object):
    """
    Abstract datasource class for retrieving market data using data providers.

    :param config a dictionary containing configuration values
    :type config: dict
        isLibrary: is the underlying data source a python library
                        bool, default False, optional
        isAuth: Is the data source authenticated. If :keyword True, token should be provided
                        bool, default True, optional
        retryCount
        retryDelay
        baseUrl: str, default None, required if is_lib is False
            Base url of the data source API
        version: str, default None, optional
            Version of the API
        token: str, optional
            Authentication token for the data source
        tokenEnv: str, default "DATASOURCE_TOKEN" (if token is None), optional
            API token can be configured as an environment variable. In that instance,
            the environment variable name can be passed using token_env attribute
    :raises AuthenticationException if token is not provided for an authenticated data source
    :rtype AuthenticationException
    """
    def __init__(self, config):
        self.is_lib = config.get("isLibrary", default=False)
        self.is_auth = config.get("isAuthenticated", default=True)

        if self.is_lib is False:
            self.base_url = config.get("baseUrl")
            self.version = config.get("version")

        if self.is_auth is True:
            self.token = config.get("authToken")
            if self.token is None:
                self.token = os.getenv(config.get("tokenEnv", default="DATASOURCE_TOKEN"))

            if not self.token or isinstance(self.token, str):
                raise AuthenticationException("Authentication token is required to proceed with the data source")

        self.retry_count = config.get("retryCount", default=3)
        self.retry_delay = config.get("retryDelay", default=0.5)

    @property
    def base_url(self):
        return self.base_url

    @base_url.setter
    def base_url(self, base_url):
        self.base_url = base_url

    @property
    def token(self):
        return self.token

    @token.setter
    def token(self, token):
        self.token = token

    def prepare_url(self, resource):
        return "%s%s" % (self.base_url, resource)

    def get_data(self, resource, params, headers):
        """


        :param resource:
        :param params:
        :param headers:
        :return:
        """
        if params is None:
            params = {}
        params["token"] = self.token
        url = self.prepare_url(resource)
        response = requests.get(url=url, params=params, headers=headers)
        logger.debug("REQUEST: %s" % response.request.url)
        logger.debug("RESPONSE: %s" % response.status_code)
        # TODO: properly handle error statuses
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            response.raise_for_status()


