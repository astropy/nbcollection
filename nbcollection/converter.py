# Standard library
import os

# Third-party
import jinja2

# Package
from nbcollection.logger import logger
from nbcollection.nb_helpers import get_title
from nbcollection.notebook import nbcollectionNotebook

__all__ = ['nbcollectionConverter']


def get_output_path(nb_path, build_path,
                    relative_root_path=None, flatten=False):
    if relative_root_path is not None:
        # relative_root_path = os.path.abspath(relative_root_path)
        common_prefix = os.path.commonpath([nb_path,
                                            relative_root_path])
        if common_prefix == '/':
            # If there is no common prefix, write all notebooks directly to
            # the build directory. This is useful for testing and, e.g.,
            # writing all executed notebooks to a temporary directory
            relative_path = ''
            # TODO: should we warn?
        else:
            relative_path = os.path.relpath(nb_path, common_prefix)
    else:
        relative_path = ''

    if flatten:  # flatten the directory structure
        full_build_path = build_path
    else:
        full_build_path = os.path.abspath(os.path.join(build_path,
                                                       relative_path))
    os.makedirs(full_build_path, exist_ok=True)
    return full_build_path


class nbcollectionConverter:
    build_dir_name = "_build"

    def __init__(self, notebooks, overwrite=False,
                 build_path=None, flatten=False,
                 execute_kwargs=None, convert_kwargs=None, **kwargs):
        """
        Parameters
        ----------
        notebooks : str, iterable
            Either a string path to a single notebook, a path to a collection of
            notebooks, or an iterable containing individual notebook files.
        overwrite : bool (optional)
        """

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
                        if d.startswith('.') or d.startswith('_'):
                            # calling remove here actually modifies the paths
                            # that os.walk will recursively explore
                            dirs.remove(d)

                    for name in files:
                        basename, ext = os.path.splitext(name)
                        file_path = os.path.join(root, name)

                        if ext == '.ipynb':
                            nb = nbcollectionNotebook(
                                file_path,
                                output_path=get_output_path(
                                    file_path, build_path=build_path,
                                    relative_root_path=self._relative_root_path,
                                    flatten=flatten),
                                overwrite=overwrite,
                                execute_kwargs=execute_kwargs,
                                convert_kwargs=convert_kwargs)
                            nbs.append(nb)

            elif os.path.isfile(notebook):
                # It's a single file:
                nb = nbcollectionNotebook(
                    notebook,
                    output_path=get_output_path(
                        notebook, build_path=build_path,
                        relative_root_path=self._relative_root_path,
                        flatten=flatten),
                    overwrite=overwrite,
                    execute_kwargs=execute_kwargs,
                    convert_kwargs=convert_kwargs)
                nbs.append(nb)

            else:
                raise ValueError("Input specification of notebooks not "
                                 "understood: File or path does not exist "
                                 f"'{notebook}'")

        logger.info(f"Collected {len(nbs)} notebook files")
        logger.debug("Executed/converted notebooks will be saved in: "
                     f"{build_path}")

        self.notebooks = nbs
        self.flatten = flatten
        self.build_path = build_path

    def execute(self, stop_on_error=False):
        exceptions = dict()
        for nb in self.notebooks:
            try:
                nb.execute()
            except Exception as e:
                if stop_on_error:
                    raise e
                exceptions[nb.filename] = e

        if exceptions:
            for nb, e in exceptions.items():
                logger.error(f"Notebook '{nb}' errored: {str(e)}")
            raise RuntimeError(f"{len(exceptions)} notebooks raised unexpected "
                               "errors while executing cells: "
                               f"{list(exceptions.keys())} — see above for "
                               "more details about the failing cells. If any "
                               "of these are expected errors, add a Jupyter "
                               "cell tag 'raises-exception' to the failing "
                               "cells.")

    def convert(self):
        for nb in self.notebooks:
            nb.convert()

    def make_html_index(self, template_file, output_filename='index.html'):
        """
        Generates an html index page for a set of notebooks

        Parameters
        ----------
        converted_files : list
            The list of paths to the notebooks
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
                autoescape=jinja2.select_autoescape(['html', 'xml']))
            templ = env.get_template(fn)

        elif isinstance(template_file, jinja2.Template):
            templ = template_file

        else:
            raise TypeError("Unknown template file type "
                            f"'{type(template_file)}'. Must be either a string "
                            "path or a jinja2 template instance.")

        out_path = os.path.dirname(output_filename)
        if out_path == '':
            # By default, write the index file to the _build/ path
            out_path = self.build_path

        notebook_metadata = []
        for nb in self.notebooks:
            relpath = os.path.relpath(nb.html_path, out_path)

            notebook_metadata.append({
                'html_path': relpath,
                'name': get_title(nb.exec_path)
            })

        content = templ.render(notebooks=notebook_metadata)
        with open(os.path.join(out_path, output_filename), 'w') as f:
            f.write(content)

        return content
