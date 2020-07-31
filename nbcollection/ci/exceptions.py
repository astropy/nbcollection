class NBCollectionCIException(Exception):
    pass

class InstallException(NBCollectionCIException):
    pass

class InvalidRepoPath(NBCollectionCIException):
    pass

class VENVValidationException(NBCollectionCIException):
    pass

class VENVInstallException(NBCollectionCIException):
    pass

