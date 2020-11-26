#!/usr/bin/env python3
# Copyright (c) 2020 embyt GmbH. See LICENSE for further details.
# Author: Roman Morawek <roman.morawek@embyt.com>
"""this is the main entry point, which sets up the Communicator class"""
import logging
import os
import traceback
import argparse

from enoceanmqtt.communicator import Communicator
from enoceanmqtt.config import SensorConfig

conf = {
    'debug': False,
    'config': ['/etc/enoceanmqtt.conf'],
    'logfile': os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'enoceanmqtt.log')
}


def parse_args():
    """ Parse command line arguments. """
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument('--debug', help='enable console debugging',
        action='store_true')
    parser.add_argument('--logfile', help='set log file location')
    parser.add_argument('config', help='specify config file[s]', nargs='*')
    # parser.add_argument('--version', help='show application version',
    #     action='version', version='%(prog)s ' + VERSION)
    args = vars(parser.parse_args())
    # logging.info('Read arguments: ' + str(args))
    return args


def setup_logging(log_filename='', log_file_level=logging.INFO, debug=False):
    # create formatter
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    # set root logger to lowest log level
    logging.getLogger().setLevel(logging.DEBUG if debug else log_file_level)

    # create console and log file handlers and the formatter to the handlers
    log_console = logging.StreamHandler()
    log_console.setFormatter(log_formatter)
    log_console.setLevel(logging.DEBUG if debug else logging.ERROR)
    logging.getLogger().addHandler(log_console)
    if log_filename:
        log_file = logging.FileHandler(log_filename)
        log_file.setLevel(log_file_level)
        log_file.setFormatter(log_formatter)
        logging.getLogger().addHandler(log_file)
        logging.info("Logging to file: {}".format(log_filename))
    if debug:
        logging.info("Logging debug to console")


def main():
    """entry point if called as an executable"""
    # logging.getLogger().setLevel(logging.DEBUG)
    # Parse command line arguments
    conf.update(parse_args())

    # setup logger
    setup_logging(conf['logfile'], debug=conf['debug'])

    # load config file
    if len(conf['config']) > 1:
        logging.warning("Multiple config files set, using {}".format(conf['config'][-1]))

    config = SensorConfig(conf['config'][-1])

    # start working
    com = Communicator(config)
    try:
        com.run()

    # catch all possible exceptions
    except:     # pylint: disable=broad-except
        logging.error(traceback.format_exc())


# check for execution
if __name__ == "__main__":
    main()
