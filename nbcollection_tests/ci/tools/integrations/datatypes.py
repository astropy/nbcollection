import enum


class RepoType(enum.Enum):
    Github = 'github-repo'
    Local = 'local-repo'


class Template(enum.Enum):
    MultiLevelIgnore = 'multi-level-ignore'
    SingleCollection = 'single-collection'
    MultiCollection = 'multi-collection'
    SingleCollectionImmediateCategories = 'single-collection-immediate-categories'
    SingleCollectionNthCategories = 'single-collection-nth-categories'
    QuickBuild = 'quick-build-collection'
    ExecutedCollection = 'executed-collection'
    MultiNotebookCategory = 'multi-notebook-category'
    MetadataRichNotebooks = 'metadata-rich-notebooks'
    EmptyDirWithGitRemoteUpstream = 'empty-dir-with-git-remote-upstream'
    NextDirWithGitRemoteUpstream = 'next-dir-with-git-remote-upstream'
    OnlyGitConfigFile = 'only-git-config-file'
