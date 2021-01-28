class AuthenticationException(Exception):
    """
    Raised when authentication error occurred when fetching data from the data source
    """
    def __init__(self, message=None, *args):
        super().__init__(message, args)


class DataSourceException(Exception):
    """
    Raised when error occurred while datasource operations are carried out
    """
    def __init__(self, message=None, *args):
        super().__init__(message, args)
