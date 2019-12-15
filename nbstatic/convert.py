# Standard library
import os
import re
import time

# Third-party
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
from nbconvert.exporters import RSTExporter
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

        os.makedirs(build_path, exist_ok=True)

        # First, get the path and notebook filename separately:
        self.nb_file_path = os.path.abspath(nb_file_path)
        nb_path, nb_filename = os.path.split(self.nb_file_path)

        # We need the notebook basename to construct the executed notebook name
        # and the rendered HTML page name:
        basename = os.path.splitext(nb_filename)[0]

        # Get the path containing the build path:
        build_path_up_one = os.path.abspath(os.path.join(build_path, '..'))

        common_prefix = os.path.commonpath([nb_path, build_path_up_one])
        if common_prefix == '/':
            # If there is no common prefix, write all notebooks directly to the
            # build directory. This is useful for testing and, e.g., writing all
            # executed notebooks to a temporary directory
            relative_path = ''
        else:
            relative_path = os.path.relpath(nb_path, common_prefix)

        self.nb_exec_path = os.path.abspath(
            os.path.join(build_path, relative_path, f"exec_{basename}.ipynb"))
        self.nb_html_path = os.path.abspath(
            os.path.join(build_path, relative_path, f"{basename}.html"))

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
            logger.debug(f"Executed notebook already exists at "
                         "'self.nb_exec_path'. Use overwrite=True or set the config item exec_overwrite=True to overwrite.")
            return self.nb_exec_path

        # Execute the notebook
        if kwargs:
            logger.debug(f'Executing notebook using kwargs {kwargs}')
        t0 = time.time()
        executor = ExecutePreprocessor(**kwargs)

        with open(self.nb_file_path) as f:
            nb = nbformat.read(f, as_version=NBFORMAT_VERSION)

        try:
            executor.preprocess(nb, {'metadata': {'path': self.path_only}})
        except CellExecutionError:
            # TODO: should we fail fast and raise, or record all errors?
            raise

        logger.info("Finished running notebook ({:.2f} seconds)"
                    .format(time.time() - t0))

        if write:
            logger.debug('Writing executed notebook to file {0}...'
                         .format(self._executed_nb_path))
            with open(self._executed_nb_path, 'w') as f:
                nbformat.write(nb, f)

            return self._executed_nb_path


class NBStaticConverter:

    def __init__(self, nb_path, output_path=None, template_file=None,
                 overwrite=False, kernel_name=None):
        self.nb_path = path.abspath(nb_path)
        fn = path.basename(self.nb_path)
        self.path_only = path.dirname(self.nb_path)
        self.nb_name, _ = path.splitext(fn)

        if output_path is not None:
            self.output_path = output_path
            makedirs(self.output_path, exist_ok=True)
        else:
            self.output_path = self.path_only

        if template_file is not None:
            self.template_file = path.abspath(template_file)
        else:
            self.template_file = None

        self.overwrite = overwrite

        # the executed notebook
        self._executed_nb_path = path.join(self.output_path,
                                           'exec_{0}'.format(fn))

        logger.info('Processing notebook {0} (in {1})'.format(fn,
                                                              self.path_only))

        self._execute_kwargs = dict(timeout=900)
        if kernel_name:
            self._execute_kwargs['kernel_name'] = kernel_name

    def execute(self, write=True):
        """
        Execute the specified notebook file, and optionally write out the
        executed notebook to a new file.

        Parameters
        ----------
        write : bool, optional
            Write the executed notebook to a new file, or not.

        Returns
        -------
        executed_nb_path : str, ``None``
            The path to the executed notebook path, or ``None`` if
            ``write=False``.

        """

        if path.exists(self._executed_nb_path) and not self.overwrite:
            logger.debug("Executed notebook already exists at {0}. Use "
                         "overwrite=True or --overwrite (at cmd line) to re-run"
                         .format(self._executed_nb_path))
            return self._executed_nb_path

        # Execute the notebook
        logger.debug('Executing notebook using kwargs '
                     '"{}"...'.format(self._execute_kwargs))
        t0 = time.time()
        executor = ExecutePreprocessor(**self._execute_kwargs)

        with open(self.nb_path) as f:
            nb = nbformat.read(f, as_version=IPYTHON_VERSION)

        try:
            executor.preprocess(nb, {'metadata': {'path': self.path_only}})
        except CellExecutionError:
            # TODO: should we fail fast and raise, or record all errors?
            raise

        logger.info("Finished running notebook ({:.2f} seconds)"
                    .format(time.time() - t0))

        if write:
            logger.debug('Writing executed notebook to file {0}...'
                         .format(self._executed_nb_path))
            with open(self._executed_nb_path, 'w') as f:
                nbformat.write(nb, f)

            return self._executed_nb_path

    def convert(self, remove_executed=False):
        """
        Convert the executed notebook to a restructured text (RST) file.

        Parameters
        ----------
        delete_executed : bool, optional
            Controls whether to remove the executed notebook or not.
        """

        if not path.exists(self._executed_nb_path):
            raise IOError("Executed notebook file doesn't exist! Expected: {0}"
                          .format(self._executed_nb_path))

        if path.exists(self._rst_path) and not self.overwrite:
            logger.debug("RST version of notebook already exists at {0}. Use "
                         "overwrite=True or --overwrite (at cmd line) to re-run"
                         .format(self._rst_path))
            return self._rst_path

        # Initialize the resources dict - see:
        # https://github.com/jupyter/nbconvert/blob/master/nbconvert/nbconvertapp.py#L327
        resources = {}
        resources['config_dir'] = '' # we don't need to specify config
        resources['unique_key'] = self.nb_name

        # path to store extra files, like plots generated
        resources['output_files_dir'] = 'nboutput'

        # these keywords are used to build the filter keywords
        # TODO: add a pre-processor that extracts the keywords from the markdown
        # cell in the header and adds them to this list
        # NOTE: the split[-4] trick below is brittle in that it will break if
        # a notebook is, say, nested two layers deep instead of just one like
        # all of our notebooks thus far.
        resources['nb_keywords'] = [self.nb_path.split(sep)[-4]]

        # Exports the notebook to RST
        logger.debug('Exporting notebook to RST...')
        exporter = RSTExporter()

        if self.template_file:
            exporter.template_file = self.template_file
        output, resources = exporter.from_filename(self._executed_nb_path,
                                                   resources=resources)

        # Write the output RST file
        writer = FilesWriter()
        output_file_path = writer.write(output, resources,
                                        notebook_name=self.nb_name)

        # read the executed notebook, grab the keywords from the header,
        # add them in to the RST as filter keywords
        with open(self._executed_nb_path) as f:
            nb = nbformat.read(f, as_version=IPYTHON_VERSION)

        top_cell_text = nb['cells'][0]['source']
        match = re.search('## [kK]eywords\s+(.*)', top_cell_text)

        if match:
            keywords = match.groups()[0].split(',')
            keywords = [clean_keyword(k) for k in keywords if k.strip()]
            keyword_filters = ['filter{0}'.format(k) for k in keywords]
        else:
            keyword_filters = []

        # Add metatags to top of RST files to get rendered into HTML, used for
        # the search and filter functionality in Learn Astropy
        meta_tutorials = '.. meta::\n    :keywords: {0}\n'
        filters = ['filterTutorials'] + keyword_filters
        meta_tutorials = meta_tutorials.format(', '.join(filters))
        with open(output_file_path, 'r') as f:
            rst_text = f.read()

        with open(output_file_path, 'w') as f:
            rst_text = '{0}\n{1}'.format(meta_tutorials, rst_text)
            f.write(rst_text)

        if remove_executed: # optionally, clean up the executed notebook file
            remove(self._executed_nb_path)

        return output_file_path

def process_notebooks(nbfile_or_path, exec_only=False, verbosity=None,
                      **kwargs):
    """
    Execute and optionally convert the specified notebook file or directory of
    notebook files.

    This is a wrapper around the ``NBTutorialsConverter`` class that does file
    handling.

    Parameters
    ----------
    nbfile_or_path : str
        Either a single notebook filename or a path containing notebook files.
    exec_only : bool, optional
        Just execute the notebooks, don't run them.
    verbosity : int, optional
        A ``logging`` verbosity level, e.g., logging.DEBUG or etc. to specify
        the log level.
    **kwargs
        Any other keyword arguments are passed to the ``NBTutorialsConverter``
        init.

    """
    if verbosity is not None:
        logger.setLevel(verbosity)

    if path.isdir(nbfile_or_path):
        # It's a path, so we need to walk through recursively and find any
        # notebook files
        for root, dirs, files in walk(nbfile_or_path):
            for name in files:
                _,ext = path.splitext(name)
                full_path = path.join(root, name)

                if 'ipynb_checkpoints' in full_path: # skip checkpoint saves
                    continue

                if name.startswith('exec'): # notebook already executed
                    continue

                if ext == '.ipynb':
                    nbc = NBTutorialsConverter(full_path, **kwargs)
                    nbc.execute()

                    if not exec_only:
                        nbc.convert()

    else:
        # It's a single file, so convert it
        nbc = NBTutorialsConverter(nbfile_or_path, **kwargs)
        nbc.execute()

        if not exec_only:
            nbc.convert()

if __name__ == "__main__":
    from argparse import ArgumentParser
    import logging

    # Define parser object
    parser = ArgumentParser(description="")

    vq_group = parser.add_mutually_exclusive_group()
    vq_group.add_argument('-v', '--verbose', action='count', default=0,
                          dest='verbosity')
    vq_group.add_argument('-q', '--quiet', action='count', default=0,
                          dest='quietness')

    parser.add_argument('--exec-only', default=False, action='store_true',
                        dest='exec_only', help='Just execute the notebooks, '
                                               'don\'t convert them as well. '
                                               'This is useful for testing that'
                                               ' the notebooks run.')

    parser.add_argument('-o', '--overwrite', action='store_true',
                        dest='overwrite', default=False,
                        help='Re-run and overwrite any existing executed '
                             'notebook or RST files.')

    parser.add_argument('nbfile_or_path', default='tutorials/notebooks/',
                        nargs='?',
                        help='Path to a specific notebook file, or the '
                             'top-level path to a directory containing '
                             'notebook files to process.')

    parser.add_argument('--template', default=None, dest='template_file',
                        help='The path to a jinja2 template file for the '
                             'notebook to RST conversion.')

    parser.add_argument('--output-path', default=None, dest='output_path',
                        help='The path to save all executed or converted '
                             'notebook files. If not specified, the executed/'
                             'converted files will be in the same path as the '
                             'source notebooks.')

    parser.add_argument('--kernel-name', default='python3', dest='kernel_name',
                        help='The name of the kernel to run the notebooks with.'
                             ' Must be an available kernel from "jupyter '
                             'kernelspec list".')

    args = parser.parse_args()

    # Set logger level based on verbose flags
    if args.verbosity != 0:
        if args.verbosity == 1:
            logger.setLevel(logging.DEBUG)
        else: # anything >= 2
            logger.setLevel(1)

    elif args.quietness != 0:
        if args.quietness == 1:
            logger.setLevel(logging.WARNING)
        else: # anything >= 2
            logger.setLevel(logging.ERROR)

    # make sure output path exists
    output_path = args.output_path
    if output_path is not None:
        output_path = path.abspath(output_path)
        makedirs(output_path, exist_ok=True)

    # make sure the template file exists
    template_file = args.template_file
    if template_file is not None and not path.exists(template_file):
        raise IOError("Couldn't find RST template file at {0}"
                      .format(template_file))

    process_notebooks(args.nbfile_or_path, exec_only=args.exec_only,
                      output_path=output_path, template_file=template_file,
                      overwrite=args.overwrite, kernel_name=args.kernel_name)
