import time

import requests
from setup_logs import log
from telegram import send_telegram


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
