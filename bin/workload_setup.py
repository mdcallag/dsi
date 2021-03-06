#!/usr/bin/env python3
"""
Setup hosts for running various kinds of workload types
"""

import argparse
import logging
import sys

from common.delays import safe_reset_all_delays
import common.host_utils
import common.command_runner
from common.config import ConfigDict
from common.log import setup_logging

LOG = logging.getLogger(__name__)


class WorkloadSetupRunner(object):
    """
    Responsible for invoking workload_setup.yml commands before test_control
    """
    def __init__(self, config):
        """
        Constructor.

        :param config: The system configuration
        """
        self.config = config

    def test_types(self):
        """
        Indicates which test types we have in test_control.

        :return: Test-types for which we need to run the associated workload_setup blocks
        :rtype: set(string)
        """
        return set([run['type'] for run in self.config['test_control']['run']])

    def setup_workloads(self):
        """
        Perform setup for all the required workload types
        """
        common.host_utils.setup_ssh_agent(self.config)
        for test_type in self.test_types():
            self.run_setup_for_test_type(test_type)

    def run_setup_for_test_type(self, test_type):
        """
        Run setup for a particular test type.

        :param string test_type: Workload_setup key listing commands to run
        """
        LOG.info("Starting workload_setup for test_type %s", test_type)
        steps = self.config['workload_setup'][test_type]
        common.command_runner.run_host_commands(steps, self.config, 'workload_setup')


def main(argv):
    """
    Parse args and call workload_setup.yml operations
    """
    parser = argparse.ArgumentParser(description='Workload Setup')

    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output')
    parser.add_argument('--log-file', help='path to log file')

    args = parser.parse_args(argv)
    setup_logging(args.debug, args.log_file)

    config = ConfigDict('workload_setup')
    config.load()

    # Delays should be unset at the end of each test_control.py run, but if it didn't complete...
    safe_reset_all_delays(config)

    setup = WorkloadSetupRunner(config)
    setup.setup_workloads()


if __name__ == '__main__':
    main(sys.argv[1:])
