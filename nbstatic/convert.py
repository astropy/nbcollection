# Standard library
import os
import re
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
            print("DERP")
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

        logger.info("Finished running notebook ({:.2f} seconds)"
                    .format(time.time() - t0))

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


# TODO:
# self._execute_kwargs = dict(timeout=900)

class NBStaticConverter:

    def __init__(self, root_nb_path, template_file=None, overwrite=False):
        pass


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
