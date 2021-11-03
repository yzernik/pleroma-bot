import re
import time
import json
import string
import random
import requests
import threading
import functools
import mimetypes

from queue import Queue
from itertools import cycle
from json.decoder import JSONDecodeError
from datetime import datetime, timedelta

# Try to import libmagic
# if it fails just use mimetypes
try:
    import magic
except ImportError:
    magic = None

from .i18n import _
from . import logger


class PropagatingThread(threading.Thread):
    """
    Thread that surfaces exceptions that occur inside of it
    """

    def run(self):
        self.exc = None
        # Event to keep track if thread has started
        self.started_evt = threading.Event()
        try:
            self.ret = self._target(*self._args, **self._kwargs)
            self.started_evt.set()
        except BaseException as e:
            self.exc = e
            self.started_evt.clear()

    def join(self):
        if not self.exc:
            self.started_evt.wait()
        super(PropagatingThread, self).join()
        self.started_evt.clear()
        if self.exc:
            raise self.exc
        return self.ret


def spinner(message, spinner_symbols: list = None):
    """
    Decorator that launches the function wrapped and the spinner each in a
    separate thread
    :param message: Message to display next to the spinner
    :param spinner_symbols:
    :return:
    """
    spinner_symbols = spinner_symbols or list("|/-\\")
    spinner_symbols = cycle(spinner_symbols)
    global input_thread

    def start():
        while input_thread.is_alive():
            symbol = next(spinner_symbols)
            print(
                "\r{message} {symbol}".format(message=message, symbol=symbol),
                end="",
            )
            time.sleep(0.3)

    def stop():
        print("\r", end="")

    def external(fct):
        @functools.wraps(fct)
        def wrapper(*args, **kwargs):
            return_que = Queue()
            global input_thread
            input_thread = PropagatingThread(
                target=lambda q, *arg1, **kwarg1: q.put(fct(*arg1, **kwarg1)),
                args=(return_que, *args),
                kwargs=dict(**kwargs),
            )
            input_thread.start()
            spinner_thread = threading.Thread(target=start)
            spinner_thread.start()

            spinner_thread.join()
            input_thread.join()
            stop()

            result = return_que.get()

            return result

        return wrapper

    return external


def replace_vars_in_str(self, text: str, var_name: str = None) -> str:
    """
    Returns a string with "{{ var_name }}" replaced with var_name's value
    If no 'var_name' is provided, locals() (or self if it's an object
    method) will be used and all variables found in locals() (or object
    attributes) will be replaced with their values.

    :param text: String to be parsed, replacing "{{ var_name }}" with
    var_name's value. Multiple occurrences are supported.
    :type text: str
    :param var_name: Name of the variable to be replace. Multiple
    occurrences are supported. If not provided, locals() will be used and
    all variables will be replaced with their values.
    :type var_name: str

    :returns: A string with {{ var_name }} replaced with var_name's value.
    :rtype: str
    """
    # Jinja-style string replacement i.e. vars encapsulated in {{ and }}
    if var_name is not None:
        matching_pattern = r"(?<=\{{)( " + var_name + r" )(?=\}})"
        matches = re.findall(matching_pattern, text)
    else:
        matches = re.findall(r"(?<={{)(.*?)(?=}})", text)
    for match in matches:
        pattern = r"{{ " + match.strip() + " }}"
        # Get attribute value if it's a method
        # go for locals() if not, fallback to globals()
        try:
            value = getattr(self, match.strip())
        except (NameError, AttributeError):
            try:
                value = locals()[match.strip()]
            except (NameError, KeyError):
                value = globals()[match.strip()]
        if isinstance(value, list):
            value = ", ".join([str(elem) for elem in value])
        text = re.sub(pattern, value, text)
    return text


def guess_type(media_file: str) -> str:
    """Try to guess what MIME type the given file is.

    :param media_file: The file to perform the guessing on
    :returns: the MIME type result of guessing
    :rtype: str
    """
    mime_type = None
    try:
        mime_type = magic.from_file(media_file, mime=True)
    except AttributeError:
        mime_type = mimetypes.guess_type(media_file)[0]
    return mime_type


def random_string(length: int) -> str:
    """Returns a string of random characters of length 'length'
    :param length: How long the string to return must be
    :type length: int
    :returns: an alpha-numerical string of specified length with random
    characters
    :rtype: str
    """
    return "".join(
        random.choice(string.ascii_lowercase + string.digits)
        for _ in range(length)
    )


def _get_instance_info(self):
    instance_url = f"{self.pleroma_base_url}/api/v1/instance"
    response = requests.get(instance_url)
    if not response.ok:
        response.raise_for_status()
    try:
        instance_info = json.loads(response.text)
    except JSONDecodeError:
        msg = _(
            "Instance response was not understood {}"
        ).format(response.text)
        raise ValueError(msg)
    if "Pleroma" not in instance_info["version"]:
        logger.debug(_("Assuming target instance is Mastodon..."))
        if len(self.display_name) > 30:
            self.display_name = self.display_name[:30]
            log_msg = _(
                "Mastodon doesn't support display names longer than 30 "
                "characters, truncating it and trying again..."
            )
            logger.warning(log_msg)
        if hasattr(self, "rich_text"):
            if self.rich_text:
                self.rich_text = False
                logger.warning(
                    _("Mastodon doesn't support rich text. Disabling it...")
                )


def force_date(self):
    logger.info(
        _("How far back should we retrieve tweets from the Twitter account?")
    )
    date_msg = _(
        "\nEnter a date (YYYY-MM-DD):"
        "\n[Leave it empty to retrieve *ALL* tweets or enter 'continue'"
        "\nif you want the bot to execute as normal (checking date of "
        "\nlast post in the Fediverse account)] "
    )
    logger.info(date_msg)
    input_date = input()
    if input_date == "continue":
        if self.posts != "none_found":
            date = self.get_date_last_pleroma_post()
        else:
            date = datetime.strftime(
                datetime.now() - timedelta(days=2), "%Y-%m-%dT%H:%M:%SZ"
            )
    elif input_date is None or input_date == "":
        self.max_tweets = 100
        # Minimum date allowed
        date = "2010-11-06T00:00:00Z"
    else:
        self.max_tweets = 100
        date = datetime.strftime(
            datetime.strptime(input_date, "%Y-%m-%d"),
            "%Y-%m-%dT%H:%M:%SZ",
        )
    return date
