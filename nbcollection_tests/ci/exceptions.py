class CITestException(Exception):
    pass

class MissingENVVarException(CITestException):
    pass

class GithubInvalidAuthorization(CITestException):
    pass

class SSHInvalidAuthorization(CITestException):
    pass
