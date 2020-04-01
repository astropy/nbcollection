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
from nbstatic.nb_helpers import is_executed

__all__ = ['NBStaticNotebook']


class NBStaticNotebook:
    nbformat_version = 4

    def __init__(self, file_path, output_path=None, overwrite=False,
                 execute_kwargs=None, convert_kwargs=None):
        """
        Parameters
        ----------
        file_path : str
            The path to a notebook file
        output_path : str (optional)
            The full path to a notebook
        overwrite : bool (optional)
            Whether or not to overwrite files.
        execute_kwargs : dict (optional)
            Keyword arguments passed through to
            ``nbconvert.ExecutePreprocessor``.
        convert_kwargs : dict (optional)
            Keyword arguments passed through to ``nbconvert.HTMLExporter``.
        """

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
        self.exec_path = os.path.join(output_path, f"{self.basename}.ipynb")
        self.html_path = os.path.join(output_path, f"{self.basename}.html")

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
            logger.debug(f"Executed notebook exists at '{self.exec_path}'. "
                         "Use overwrite=True or set the config item "
                         "exec_overwrite=True to overwrite.")
            return self.exec_path

        # Execute the notebook
        logger.debug(f"Executing notebook '{self.filename}' ⏳")
        t0 = time.time()

        executor = ExecutePreprocessor(**self.execute_kwargs)
        with open(self.file_path) as f:
            nb = nbformat.read(f, as_version=self.nbformat_version)

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
