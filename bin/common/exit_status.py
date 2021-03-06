"""Module of utility functions for analysis"""

from collections import namedtuple

import os

EXIT_STATUS_OK = 0
""" This code indicates that the command did not return an error """

EXIT_STATUS_ERR = 1
""" This code indicates that the command returned an error, although it is not specific """

EXIT_STATUS_LINE_PREFIX = 'exit_status:'
""" A test output file name status must start with this prefix """


class ExitStatus(namedtuple("ExitStatus", ["status", "message"])):
    """ Class to hold exit status and message """

    __slots__ = ()
    """ https://docs.python.org/2/library/collections.html The subclass shown above sets __slots__
        to an empty tuple. This helps keep memory requirements low by preventing the creation of
        instance dictionaries.
    """
    def __str__(self):
        """ generate a human readable exit status. """
        if self.status == 0:
            result = 'Succeeded'
        else:
            result = 'Failed'

        if self.message:
            human = "Command {}: status={} message={}".format(result, self.status, self.message)
        else:
            human = "Command {}: status={}".format(result, self.status)
        return human


def write_exit_status(stream, exit_status):
    """
    print the exit status in the correct format.

    :param io stream: the io to write the status.
    :param exit_status: the process exit status or None (None indicates success).
    :type exit_status:  ErrorStatus  or None.
    """

    if exit_status is None:
        status = 0
        message = ""
    else:
        status = exit_status.status
        message = exit_status.message
        if message:
            message = message.encode('unicode_escape')
            message = message.decode('utf8')
    stream.write("\n{} {} '{}'\n".format(EXIT_STATUS_LINE_PREFIX, status, message))
    stream.flush()


def read_exit_status(filename):
    """
    read the exit status from the last line of filename.

    :param str filename: the test output filename.
    """

    stat = os.stat(filename)
    if stat.st_size:
        with open(filename, 'r') as file_handle:
            last_line = file_handle.readlines()[-1]
        if last_line.startswith(EXIT_STATUS_LINE_PREFIX):
            parts = last_line.split(' ', 2)
            if len(parts) == 1:
                status, message = (EXIT_STATUS_ERR, None)
            elif len(parts) == 2:
                status, message = (parts[1], None)
            else:
                status, message = parts[1:]
            status = int(status)
            if message:
                message = message.decode('unicode_escape')
        else:
            status = EXIT_STATUS_ERR
            message = "Unknown Error: expected status line was missing from '{}'".format(filename)
    else:
        status = EXIT_STATUS_ERR
        message = "Unknown Error: empty file '{}'".format(filename)

    return ExitStatus(status, message)
