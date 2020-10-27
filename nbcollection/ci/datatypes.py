import typing

from nbcollection.ci.constants import PWN

class IgnoreData(typing.NamedTuple):
    entries: typing.List[str]

class Collection(typing.NamedTuple):
    name: str
    path: str

class Metadata(typing.NamedTuple):
    path: str

class Notebook(typing.NamedTuple):
    name: str
    path: str
    metadata: Metadata

class Namespace(typing.NamedTuple):
    name: str

class PreRequirements(typing.NamedTuple):
    path: str

class Requirements(typing.NamedTuple):
    path: str

class PreInstall(typing.NamedTuple):
    path: str

class Category(typing.NamedTuple):
    name: str
    path: str
    collection: Collection
    notebooks: typing.List[Notebook]
    pre_requirements: Requirements
    requirements: Requirements
    namespaces: typing.List[Namespace]

class BuildJob(typing.NamedTuple):
    collection: Collection
    category: Category
    def semantic_path(self) -> PWN:
        formatted_namespaces = '/'.join([ns.name for ns in self.category.namespaces])
        if formatted_namespaces:
            return '/'.join([self.collection.name, formatted_namespaces, self.category.name])

        else:
            return '/'.join([self.collection.name, self.category.name])

class MetadataContext(typing.NamedTuple):
    path: str

class ArtifactContext(typing.NamedTuple):
    dirpath: str
    path: str
    metadata_path: str

class NotebookContext(typing.NamedTuple):
    notebook: Notebook
    collection_name: str
    category_name: str
    path: str
    build_script_path: str
    metadata: MetadataContext
    artifact: ArtifactContext

class JobContext(typing.NamedTuple):
    build_dir: str
    setup_script: str
    # build_scripts: typing.List[str]
    notebooks: typing.List[NotebookContext]
    job: BuildJob
    pre_install: PreInstall
    pre_requirements: PreRequirements
    requirements: Requirements
    logfile_name: str

class BuildContext(typing.NamedTuple):
    build_dir: str
    output_format: str
    timeout: int = 600
