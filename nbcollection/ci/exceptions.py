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

class RendererException(NBCollectionCIException):
    pass

class BuildError(NBCollectionCIException):
    pass

class MetadataExtractionError(NBCollectionCIException):
    pass
