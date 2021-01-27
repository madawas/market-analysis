class AuthenticationException(Exception):
    """
    This exception is thrown when there is an issue with authenticating
    with the data source
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg