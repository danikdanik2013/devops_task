import os
import sys

from setup import APP_PORT

MIN_PYTHON = (3, 6)


def root_check():
    """
    Func for checking root run
    :return: None
    """
    if not os.geteuid() == 0:
        sys.exit("\nOnly root can run this script\n")


def check_port():
    """
    Func for check port for app
    :return: None
    """
    if not APP_PORT:
        sys.exit("\nPlease, specify APP_PORT configuration\n")


def arg_parse():
    """
    Func for check args
    :return: None
    """
    if len(sys.argv) <= 1:
        sys.exit("\nPlease, enter the directory\n")


def python_check():
    """
    Func for check version of python. Python must be 3.6+
    :return: None
    """
    if not sys.version_info >= MIN_PYTHON:
        sys.exit()


def before_start():
    """
    Manage func for start processes
    :return:
    """
    python_check()
    root_check()
    arg_parse()
    check_port()
