"""
Simple module to help take care of everything needed for pushing
a message to pushover. I may look into packaging this later on for PyPI
"""
import os

import requests

api = "https://api.pushover.net/1/messages.json"

user_key = os.environ['PUSHOVER_USER'] if 'PUSHOVER_USER' in os.environ else None
app_key  = os.environ['PUSHOVER_APP'] if 'PUSHOVER_APP' in os.environ else None


class PushoverException(Exception): pass


def pushover(message, title="", timestamp="", device="", url="",
             url_title="", priority=0, sound="",
             user_key=user_key, app_key=app_key):
    """
    Adds a new notification to the queue, but fails if the message and
    title are over 512 chars long, or if the url is over 500 chars long,
    or the url_title is over 50 chars long, per specs of the pushover API.

    For information about the parameters, please see:
        https://pushover.net/api

    :param app_key: Your pushover application key, this can either be passed
      or it can be stored in the env. as PUSHOVER_APP
    :param user_key: Your pushover user key, again this can be passed or
      stored in PUSHOVER_USER
    """
    if not app_key:
        raise PushoverException("No pushover app key supplied")

    if not user_key:
        raise PushoverException("No pushover user key supplied")

    if len(message + title) > 512:
        raise PushoverException("""Message over 512 characters long.\
                                   Skipping adding to queue""")

    if url and len(url) > 500:
        raise PushoverException("""URL cannot be over 500 characters long.\
                                   Skipping adding to queue""")

    if url_title and len(url_title) > 50:
        raise PushoverException("""URL titles cannot be over 50\
                                   characters long. Skipping adding\
                                   to queue""")

    pushover_data = {
        "token":   app_key,
        "user":    user_key,
        "message": message
    }

    if title:     pushover_data["title"]     = title
    if timestamp: pushover_data["timestamp"] = timestamp
    if device:    pushover_data["device"]    = device
    if url:       pushover_data["url"]       = url
    if url_title: pushover_data["url_title"] = url_title
    if priority:  pushover_data["priority"]  = priority
    if sound:     pushover_data["sound"]     = sound

    result = requests.post(api, pushover_data).json()

    if result["status"] != 1:
        raise PushoverException("Something went wrong!: %s"
                                 % result["errors"])

    return result
