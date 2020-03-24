# Standard library
import os
import time

# Third-party
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
from nbconvert.exporters import HTMLExporter
from nbconvert.writers import FilesWriter
import nbformat

# Package
from nbstatic.logger import logger

BUILD_DIR_NAME = "_build"
NBFORMAT_VERSION = 4


class NBStaticNotebook:

    def __init__(self, nb_file_path, build_path, relative_root_path=None,
                 flatten=False, overwrite=False, **kwargs):
        if not os.path.exists(nb_file_path):
            raise IOError(f"Notebook file '{nb_file_path}' does not exist")

        if not os.path.isfile(nb_file_path):
            raise ValueError("Input notebook path must contain a filename, "
                             "e.g., /path/to/some/notebook.ipynb (I received: "
                             f"{nb_file_path})")

        # First, get the path and notebook filename separately:
        self.nb_file_path = os.path.abspath(nb_file_path)
        self.nb_path, self.nb_filename = os.path.split(self.nb_file_path)

        # We need the notebook basename to construct the executed notebook name
        # and the rendered HTML page name:
        self.nb_basename = os.path.splitext(self.nb_filename)[0]

        if relative_root_path is not None:
            relative_root_path = os.path.abspath(relative_root_path)
            common_prefix = os.path.commonpath([self.nb_path,
                                                relative_root_path])
            if common_prefix == '/':
                # If there is no common prefix, write all notebooks directly to
                # the build directory. This is useful for testing and, e.g.,
                # writing all executed notebooks to a temporary directory
                relative_path = ''
                # TODO: should I warn?
            else:
                relative_path = os.path.relpath(self.nb_path, common_prefix)
        else:
            relative_path = ''

        if flatten:  # flatten the directory structure
            full_build_path = build_path
        else:
            full_build_path = os.path.abspath(os.path.join(build_path,
                                                           relative_path))
        os.makedirs(full_build_path, exist_ok=True)

        self.nb_exec_path = os.path.join(full_build_path,
                                         f"{self.nb_basename}.ipynb")
        self.nb_html_path = os.path.join(full_build_path,
                                         f"{self.nb_basename}.html")

        self.overwrite = overwrite
        self.flatten = flatten

        self.template_file = kwargs.get('template', None)

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

        if os.path.exists(self.nb_exec_path) and not self.overwrite:
            logger.debug("Executed notebook already exists at "
                         f"'{self.nb_exec_path}'. Use overwrite=True or set "
                         "the config item exec_overwrite=True to overwrite.")
            return self.nb_exec_path

        # Execute the notebook
        t0 = time.time()
        executor = ExecutePreprocessor(kernel_name='python3')  # TODO: fix kernel

        with open(self.nb_file_path) as f:
            nb = nbformat.read(f, as_version=NBFORMAT_VERSION)

        try:
            executor.preprocess(nb, {'metadata': {'path': self.nb_path}})
        except CellExecutionError:
            logger.error(f"Notebook '{self.nb_filename}' errored ❌")
            raise

        run_time = time.time() - t0
        logger.info(f"Finished running notebook '{self.nb_filename}' "
                    f"({run_time:.2f} seconds) ✅")

        logger.debug(f'Writing executed notebook to file {self.nb_exec_path}')
        with open(self.nb_exec_path, 'w') as f:
            nbformat.write(nb, f)

        return self.nb_exec_path

    def convert(self):
        """Convert the executed notebook to a static HTML file.

        Parameters
        ----------
        """

        if not os.path.exists(self.nb_exec_path):
            raise IOError("Executed notebook file doesn't exist at "
                          f"{self.nb_exec_path} - did you execute it yet?")

        if os.path.exists(self.nb_html_path) and not self.overwrite:
            logger.debug("Rendered notebook page already exists at "
                         f"{self.nb_html_path}. Use overwrite=True to "
                         "overwrite.")
            return self.nb_html_path

        # Initialize the resources dict - see:
        # https://github.com/jupyter/nbconvert/blob/master/nbconvert/nbconvertapp.py#L327
        resources = {}
        resources['config_dir'] = ''  # we don't need to specify config
        resources['unique_key'] = self.nb_filename

        # path to store extra files, like plots generated
        resources['output_files_dir'] = 'nboutput'

        # Exports the notebook to HTML
        logger.debug('Exporting notebook to HTML...')
        exporter = HTMLExporter()

        if self.template_file:
            exporter.template_file = self.template_file
        output, resources = exporter.from_filename(self.nb_exec_path,
                                                   resources=resources)

        # Write the output HTML file
        writer = FilesWriter()
        output_file_path = writer.write(output, resources,
                                        notebook_name=self.nb_basename)

        return output_file_path


class NBStaticConverter:

    def __init__(self, notebooks, overwrite=False, **kwargs):
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
            relative_root_path = nb_path

        else:
            # Multiple paths were specified as a list, so we can't infer the
            # build path location - default to using the cwd:
            default_build_path = os.path.join(os.getcwd(), BUILD_DIR_NAME)
            relative_root_path = None

        build_path = kwargs.pop('build_path')
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
                                file_path, build_path=build_path,
                                relative_root_path=relative_root_path, **kwargs)
                            nbs.append(nb)

            elif os.path.isfile(notebook):
                # It's a single file:
                nb = NBStaticNotebook(notebook, build_path=build_path, **kwargs)
                nbs.append(nb)

            else:
                raise ValueError("Input specification of notebooks not "
                                 f"understood: {notebook}")

        logger.info(f"Collected {len(nbs)} notebooks to convert")
        logger.debug("Executed/converted notebooks will be saved in: "
                     f"{build_path}")

        self.notebooks = nbs

    def execute(self, stop_on_error=False):
        exceptions = dict()
        for nb in self.notebooks:
            try:
                nb.execute()
            except Exception as e:
                if stop_on_error:
                    raise e
                exceptions[nb.nb_filename] = e

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
