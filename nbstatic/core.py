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

    def __init__(self, nb_file_path, build_path):
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

        # Get the path containing the build path:
        build_path_up_one = os.path.abspath(os.path.join(build_path, '..'))

        common_prefix = os.path.commonpath([self.nb_path, build_path_up_one])
        if common_prefix == '/':
            # If there is no common prefix, write all notebooks directly to the
            # build directory. This is useful for testing and, e.g., writing all
            # executed notebooks to a temporary directory
            relative_path = ''
        else:
            relative_path = os.path.relpath(self.nb_path, common_prefix)

        full_build_path = os.path.abspath(os.path.join(build_path,
                                                       relative_path))
        os.makedirs(full_build_path, exist_ok=True)

        self.nb_exec_path = os.path.join(full_build_path,
                                         f"exec_{self.nb_basename}.ipynb")
        self.nb_html_path = os.path.join(full_build_path,
                                         f"{self.nb_basename}.html")

    def execute(self, overwrite=False, **kwargs):
        """Execute this notebook file and write out the executed contents to a
        new file.

        Parameters
        ----------
        overwrite : bool, optional
            Whether or not to overwrite an existing executed notebook file.
        **kwargs
            Additional keyword arguments are passed to the
            `nbconvert.preprocessors.ExecutePreprocessor` initializer.

        Returns
        -------
        executed_nb_path : str, ``None``
            The path to the executed notebook.

        """

        if os.path.exists(self.nb_exec_path) and not overwrite:
            logger.debug("Executed notebook already exists at "
                         f"'{self.nb_exec_path}'. Use overwrite=True or set "
                         "the config item exec_overwrite=True to overwrite.")
            return self.nb_exec_path

        # Execute the notebook
        if kwargs:
            logger.debug(f'Executing notebook using kwargs {kwargs}')
        t0 = time.time()
        executor = ExecutePreprocessor(**kwargs)

        with open(self.nb_file_path) as f:
            nb = nbformat.read(f, as_version=NBFORMAT_VERSION)

        try:
            executor.preprocess(nb, {'metadata': {'path': self.nb_path}})
        except CellExecutionError:
            # TODO: should we fail fast and raise, or record all errors?
            raise

        logger.info(f"Finished running notebook '{self.nb_filename}' "
                    "({:.2f} seconds)".format(time.time() - t0))

        logger.debug(f'Writing executed notebook to file {self.nb_exec_path}')
        with open(self.nb_exec_path, 'w') as f:
            nbformat.write(nb, f)

        return self.nb_exec_path

    def convert(self, overwrite=False):
        """Convert the executed notebook to a static HTML file.

        Parameters
        ----------
        """

        if not os.path.exists(self.nb_exec_path):
            raise IOError("Executed notebook file doesn't exist at "
                          f"{self.nb_exec_path} - did you run .execute() yet?")

        if os.path.exists(self.nb_html_path) and not overwrite:
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

        # TODO: figure out template-ing...
        # if self.template_file:
        #     exporter.template_file = self.template_file
        output, resources = exporter.from_filename(self.nb_exec_path,
                                                   resources=resources)

        # Write the output HTML file
        writer = FilesWriter()
        output_file_path = writer.write(output, resources,
                                        notebook_name=self.nb_basename)

        return output_file_path


class NBStaticConverter:

    def __init__(self, root_nb_path, overwrite=False):
        # This works whether the input is a single notebook file or a directory
        # containing notebooks:
        build_path = os.path.join(os.path.split(root_nb_path)[0],
                                  BUILD_DIR_NAME)

        notebooks = []
        if os.path.isdir(root_nb_path):
            # It's a directory, so we need to walk through recursively and find
            # any notebook files
            for root, dirs, files in os.walk(root_nb_path):
                for d in dirs:
                    if d.startswith('.') or d.startswith('_'):
                        # calling remove here actually modifies the paths that
                        # os.walk will recursively explore
                        dirs.remove(d)

                for name in files:
                    basename, ext = os.path.splitext(name)
                    file_path = os.path.join(root, name)

                    if ext == '.ipynb':
                        notebooks.append(NBStaticNotebook(file_path,
                                                          build_path))

        elif os.path.isfile(root_nb_path):
            # It's a single file:
            notebooks.append(NBStaticNotebook(root_nb_path, build_path))

        else:
            raise ValueError("Invalid input: must either be a notebook file or "
                             "a directory containing notebook files.")

        logger.info(f"Collected {len(notebooks)} notebooks to convert")

        self.notebooks = notebooks

    def execute(self, stop_on_error=False, overwrite=False, **kwargs):
        exceptions = dict()
        for nb in self.notebooks:
            try:
                nb.execute(overwrite=overwrite, **kwargs)
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

    def convert(self, overwrite=False, **kwargs):
        for nb in self.notebooks:
            nb.convert(overwrite=overwrite, **kwargs)
