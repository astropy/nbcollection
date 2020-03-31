# Standard library
import os
import time

# Third-party
import jinja2
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
from nbconvert.exporters import HTMLExporter
from nbconvert.writers import FilesWriter
import nbformat

# Package
from nbstatic.logger import logger
from nbstatic.nb_helpers import is_executed, get_title

BUILD_DIR_NAME = "_build"
NBFORMAT_VERSION = 4


class NBStaticNotebook:

    def __init__(self, file_path, output_path=None, overwrite=False,
                 execute_kwargs=None, convert_kwargs=None):

        if not os.path.exists(file_path):
            raise IOError(f"Notebook file '{file_path}' does not exist")

        if not os.path.isfile(file_path):
            raise ValueError("Input notebook path must contain a filename, "
                             "e.g., /path/to/some/notebook.ipynb (received: "
                             f"{file_path})")

        # First, get the path and notebook filename separately:
        self.file_path = os.path.abspath(file_path)
        self.path, self.filename = os.path.split(self.file_path)

        # If no output path is specified, use the notebook path:
        if output_path is None:
            output_path = self.path

        # Get the notebook basename to construct the rendered HTML filename:
        self.basename = os.path.splitext(self.filename)[0]

        # Paths to executed and converted HTML notebook files:
        self.exec_path = os.path.join(output_path,
                                      f"{self.basename}.ipynb")
        self.html_path = os.path.join(output_path,
                                      f"{self.basename}.html")

        self.overwrite = overwrite

        if execute_kwargs is None:
            execute_kwargs = dict()
        self.execute_kwargs = execute_kwargs

        if convert_kwargs is None:
            convert_kwargs = dict()
        self.convert_kwargs = convert_kwargs

    def execute(self):
        """Execute this notebook file and write out the executed contents to a
        new file.

        Parameters
        ----------
        overwrite : bool, optional
            Whether or not to overwrite an existing executed notebook file.

        Returns
        -------
        executed_nb_path : str, ``None``
            The path to the executed notebook.

        """

        if (os.path.exists(self.exec_path)
                and is_executed(self.exec_path)
                and not self.overwrite):
            logger.debug("Executed notebook already exists at "
                         f"'{self.exec_path}'. Use overwrite=True or set "
                         "the config item exec_overwrite=True to overwrite.")
            return self.exec_path

        # Execute the notebook
        logger.debug(f"Executing notebook '{self.filename}' ⏳")
        t0 = time.time()

        executor = ExecutePreprocessor(**self.execute_kwargs)
        with open(self.file_path) as f:
            nb = nbformat.read(f, as_version=NBFORMAT_VERSION)

        try:
            executor.preprocess(nb, {'metadata': {'path': self.path}})
        except CellExecutionError:
            logger.error(f"Notebook '{self.filename}' errored ❌")
            raise

        run_time = time.time() - t0
        logger.info(f"Finished running notebook '{self.filename}' "
                    f"({run_time:.2f} seconds) ✅")

        logger.debug(f'Writing executed notebook to file {self.exec_path}')
        with open(self.exec_path, 'w') as f:
            nbformat.write(nb, f)

        return self.exec_path

    def convert(self):
        """Convert the executed notebook to a static HTML file.

        Parameters
        ----------
        """

        self.execute()

        if os.path.exists(self.html_path) and not self.overwrite:
            logger.debug("Rendered notebook page already exists at "
                         f"{self.html_path}. Use overwrite=True to "
                         "overwrite.")
            return self.html_path

        # Initialize the resources dict:
        resources = {}
        resources['config_dir'] = ''  # we don't need to specify config
        resources['unique_key'] = self.filename

        # path to store extra files, like plots generated
        resources['output_files_dir'] = 'nboutput'

        # Exports the notebook to HTML
        logger.debug('Exporting notebook to HTML...')
        exporter = HTMLExporter(**self.convert_kwargs)
        output, resources = exporter.from_filename(self.exec_path,
                                                   resources=resources)

        # Write the output HTML file
        writer = FilesWriter()
        output_file_path = writer.write(output, resources,
                                        notebook_name=self.basename)

        return output_file_path


def get_output_path(nb_path, build_path,
                    relative_root_path=None, flatten=False):
    if relative_root_path is not None:
        relative_root_path = os.path.abspath(relative_root_path)
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


class NBStaticConverter:

    def __init__(self, notebooks, overwrite=False,
                 build_path=None, flatten=False,
                 execute_kwargs=None, convert_kwargs=None):
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
            default_build_path = os.path.join(nb_path, BUILD_DIR_NAME)
            self._relative_root_path = nb_path

        else:
            # Multiple paths were specified as a list, so we can't infer the
            # build path location - default to using the cwd:
            default_build_path = os.path.join(os.getcwd(), BUILD_DIR_NAME)
            self._relative_root_path = None

        if build_path is None:
            build_path = default_build_path
        else:
            build_path = os.path.join(build_path, BUILD_DIR_NAME)

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
                            nb = NBStaticNotebook(
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
                nb = NBStaticNotebook(
                    file_path,
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
        with open(out_path, 'w') as f:
            f.write(content)

        return content
