import enum

class RepoType(enum.Enum):
    Github = 'github-repo'
    Local = 'local-repo'

class Template(enum.Enum):
    Initial = 'initial'
    MultiLevelIgnore = 'multi-level-ignore'
    SingleCollection = 'single-collection'
    MultiCollection = 'multi-collection'
    SingleCollectionImmediateCategories = 'single-collection-immediate-categories'
    SingleCollectionNthCategories = 'single-collection-nth-categories'
    QuickBuild = 'quick-build-collection'
