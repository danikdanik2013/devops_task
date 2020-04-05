import time
import unittest

import requests

from utils.setup_logs import log
from utils.telegram import send_telegram
from setup import UNITTESTS_PATH


def simple_test():
    """
    Func for testing app inside container
    :return: None
    """
    try:
        s = requests.Session()
        url = "http://0.0.0.0:3333"
        # Need some time to up app in container
        time.sleep(2)
        response = s.get(url)
        log.info("Check the response from app")
        log.info(response)
        send_telegram(f'Request tests: {response}')

    except Exception as e:
        log.error("Build fail on tests")
        log.error(e)
        send_telegram("Build fail on tests")


def unittest_run():
    """
    Sample function for unittests
    :return: Result in stdout
    """
    if UNITTESTS_PATH:
        try:

            loader = unittest.TestLoader()
            start_dir = UNITTESTS_PATH
            suite = loader.discover(start_dir)

            runner = unittest.TextTestRunner()
            runner.run(suite)
        except Exception as e:
            log.error(e)
