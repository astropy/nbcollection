"""The nbcollection converter."""

# Standard library
import os
import re

# Third-party
import jinja2

# Package
from nbcollection.logger import logger
from nbcollection.nb_helpers import get_title
from nbcollection.notebook import NbcollectionNotebook

__all__ = ["NbcollectionConverter"]


def get_output_path(nb_path, build_path, *, relative_root_path=None, flatten=False):
    """Compute the output path for a notebook.

    Parameters
    ----------
    nb_path : str
        Path to the notebook file.
    build_path : str
        Path to the build directory.
    relative_root_path : str (optional)
        The path to the root directory containing the notebooks. This is used
        to determine the relative path to the notebook file in the output
        directory.
    flatten : bool (optional)
        Whether or not to flatten the directory structure of the output
        directory.

    Returns
    -------
    str
        The path of the output file in the build directory.
    """
    if relative_root_path is not None:
        common_prefix = os.path.commonpath([nb_path, relative_root_path])
        if common_prefix == "/":
            # If there is no common prefix, write all notebooks directly to
            # the build directory. This is useful for testing and, e.g.,
            # writing all executed notebooks to a temporary directory
            relative_path = ""
            # TODO: should we warn?
        else:
            relative_path = os.path.relpath(nb_path, common_prefix)
    else:
        relative_path = ""

    if flatten:  # flatten the directory structure
        full_build_path = build_path
    else:
        full_build_path = os.path.abspath(os.path.join(build_path, relative_path))
    os.makedirs(full_build_path, exist_ok=True)
    return full_build_path


class NbcollectionConverter:
    """A class that executes and converting a collection of notebooks.

    Parameters
    ----------
    notebooks : str, iterable
        Either a string path to a single notebook, a path to a collection of
        notebooks, or an iterable containing individual notebook files.
    overwrite : bool (optional)
    """

    build_dir_name = "_build"

    def __init__(
        self,
        notebooks,
        *,
        overwrite=False,
        build_path=None,
        flatten=False,
        exclude_pattern=None,
        include_pattern=None,
        execute_kwargs=None,
        convert_kwargs=None,
        convert_preprocessors=None,
        **kwargs,  # noqa: ARG002
    ) -> None:
        if isinstance(notebooks, str) or len(notebooks) == 1:
            if isinstance(notebooks, str):
                notebooks = [notebooks]

            # This works whether the input is a single notebook file or a
            # directory containing notebooks:
            nb_path = os.path.split(notebooks[0])[0]
            default_build_path = os.path.join(nb_path, self.build_dir_name)
            self._relative_root_path = nb_path

        else:
            # Multiple paths were specified as a list, so we can't infer the
            # build path location - default to using the cwd:
            default_build_path = os.path.join(os.getcwd(), self.build_dir_name)
            self._relative_root_path = None

        if build_path is None:
            build_path = default_build_path
        else:
            build_path = os.path.join(build_path, self.build_dir_name)

        nbs = []
        for notebook in notebooks:
            if os.path.isdir(notebook):
                # It's a directory, so we need to walk through recursively and
                # collect any notebook files
                for root, dirs, files in os.walk(notebook):
                    for d in dirs:
                        if d.startswith((".", "_")):
                            # calling remove here actually modifies the paths
                            # that os.walk will recursively explore
                            dirs.remove(d)

                    for name in files:
                        basename, ext = os.path.splitext(name)
                        file_path = os.path.join(root, name)

                        if exclude_pattern is not None and re.search(
                            exclude_pattern, name
                        ):
                            continue

                        if (
                            include_pattern is not None
                            and re.search(include_pattern, name) is None
                        ):
                            continue

                        if ext == ".ipynb":
                            nb = NbcollectionNotebook(
                                file_path,
                                output_path=get_output_path(
                                    file_path,
                                    build_path=build_path,
                                    relative_root_path=self._relative_root_path,
                                    flatten=flatten,
                                ),
                                overwrite=overwrite,
                                execute_kwargs=execute_kwargs,
                                convert_kwargs=convert_kwargs,
                                convert_preprocessors=convert_preprocessors,
                            )
                            nbs.append(nb)

            elif os.path.isfile(notebook):
                # It's a single file:
                nb = NbcollectionNotebook(
                    notebook,
                    output_path=get_output_path(
                        notebook,
                        build_path=build_path,
                        relative_root_path=self._relative_root_path,
                        flatten=flatten,
                    ),
                    overwrite=overwrite,
                    execute_kwargs=execute_kwargs,
                    convert_kwargs=convert_kwargs,
                )
                nbs.append(nb)

            else:
                msg = (
                    "Input specification of notebooks not understood: File or path "
                    f"does not exist {notebook}"
                )
                raise ValueError(msg)

        logger.info(f"Collected {len(nbs)} notebook files")
        logger.debug(f"Executed/converted notebooks will be saved in: {build_path}")

        self.notebooks = nbs
        self.flatten = flatten
        self.build_path = build_path

    def execute(self, *, stop_on_error=False):
        exceptions = {}
        for nb in self.notebooks:
            try:
                nb.execute()
            except Exception as e:
                if stop_on_error:
                    raise
                exceptions[nb.filename] = e

        if exceptions:
            for nb, exception in exceptions.items():
                logger.error(f"Notebook '{nb}' errored: {exception!s}")
            msg = (
                f"{len(exceptions)} notebooks raised unexpected errors while executing "
                f"cells: {list(exceptions.keys())} — see above for more details about "
                "the failing cells. If any of these are expected errors, add a Jupyter "
                "cell tag 'raises-exception' to the failing cells."
            )
            raise RuntimeError(msg)

    def convert(self):
        for nb in self.notebooks:
            nb.convert()

    def make_html_index(self, template_file, output_filename="index.html"):
        """Generate an html index page for a set of notebooks.

        Parameters
        ----------
        template_file : str
            A path to the template file to be used for generating the index. The
            template should be in jinja2 format and have a loop over
            ``notebook_html_paths`` to populate with the links
        output_filename : str or None
            the output file name, or None to not write the file

        Returns
        -------
        content : str
            The content of the index file
        """
        if isinstance(template_file, str):
            # Load jinja2 template for index page:
            path, fn = os.path.split(template_file)
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(path),
                autoescape=jinja2.select_autoescape(["html", "xml"]),
            )
            templ = env.get_template(fn)

        elif isinstance(template_file, jinja2.Template):
            templ = template_file

        else:
            msg = (
                f"Unknown template file type '{type(template_file)}'. Must be either a "
                "string path or a jinja2 template instance."
            )
            raise TypeError(msg)

        out_path = os.path.dirname(output_filename)
        if out_path == "":
            # By default, write the index file to the _build/ path
            out_path = self.build_path
        os.makedirs(out_path, exist_ok=True)

        notebook_metadata = []
        for nb in self.notebooks:
            relpath = os.path.relpath(nb.html_path, out_path)

            notebook_metadata.append(
                {"html_path": relpath, "name": get_title(nb.exec_path)}
            )

        content = templ.render(notebooks=notebook_metadata)
        with open(os.path.join(out_path, output_filename), "w") as f:
            f.write(content)

        return content
