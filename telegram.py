from http import HTTPStatus

import requests

from setup import TOKEN, CHANNEL_ID


def send_telegram(text: str):
    """
    Func for sending messages about build to the Telegram channel.

    :param text: message text
    :return: None
    """
    token = TOKEN
    url = "https://api.telegram.org/bot"
    channel_id = CHANNEL_ID
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
        "chat_id": channel_id,
        "text": text
    })

    if r.status_code != HTTPStatus.OK:
        raise Exception("post_text error")
