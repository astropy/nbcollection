import os
import re
import html
import traceback

from warnings import warn

class Reporter(object):
    def __init__(self):
        self.test_cases = []
        self.activated = False


    def activate(self):
        """
        Imports junit_xml and activates the reporter.
        This allows all functions with imports to execute.
        """
        self.activated = self._junit_xml_import()


    def _junit_xml_import(self):
        """
        Imports junit_xml which is required to format reports for use in CI.

        Returns True if import succeeded, False otherwise
        """
        try:
            global TestSuite, TestCase
            from junit_xml import TestSuite, TestCase
            return True
        except ImportError:
            warn('Failed to import junit_xml, required to create junit-style report.')
            return False

    @staticmethod
    def format_error(e):
        """
        Exceptions from nbconvert use ansii color escape sequences
        which are not pretty in console outputs that dont support this (jenkins).
        This function cleans up the exception message.
        """
        if isinstance(e, Exception):
            # error is an exception, format accordingly
            ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
            return html.unescape(ansi_escape.sub('',
                                ''.join(traceback.format_exception(etype=type(e),
                                value=e, tb=e.__traceback__))))
        elif isinstance(e, str):
            # error is a string
            return html.unescape(e)
        else:
            return ''


    def add_test_case(self, test_name=None, nb_name=None, nb_file=None):
        """
        Creates a new test case and adds it to list of test cases.
        """
        if self.activated:
            tc = TestCase(test_name, nb_name.replace("_", " "),
                            0, '', '', file=nb_file)
            self.test_cases.append(tc)


    def add_execution_time(self, seconds=0):
        """
        Add execution time in seconds to last test case.
        """
        if self.activated:
            self.test_cases[-1].elapsed_sec = seconds


    def add_error(self, message=None, error_type=None):
        """
        Add an error to last test case.
        """
        if self.activated:
            self.test_cases[-1].add_error_info(
                                message=self.format_error(message),
                                error_type=error_type)


    def add_std_out(self, message=None):
        """
        Add std out message to last test case.
        """
        if self.activated:
            self.test_cases[-1].stdout = self.format_error(message)


    def create_report(self, report_file=None, suite_name='Test Suite', suite_package='root'):
        """
        Create a test suite and write report to file specified
        in report_file.  Returns the resulting report string (or None if not
        activated.)
        """
        if self.activated:
            if '.xml'.casefold() not in report_file.casefold():
                report_file = report_file.split('.')[0] + '.xml'

            ts = [TestSuite(suite_name, self.test_cases, package=suite_package)]

            xmls = TestSuite.to_xml_string(ts, prettyprint=True)
            if report_file:
                if hasattr(report_file, 'write'):
                    # assume file-like
                    report_file.write(xmls)
                else:
                    # Note: depending on system, mode may need to be set to wb
                    with open(report_file, mode='w') as f:
                        f.write(xmls)
                    print('Test report written to {}'.format(os.path.abspath(f.name)))
            return xmls
