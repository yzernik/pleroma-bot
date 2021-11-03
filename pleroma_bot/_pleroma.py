import os
from json.decoder import JSONDecodeError

import json
import requests
import mimetypes
from datetime import datetime, timedelta

# Try to import libmagic
# if it fails just use mimetypes
try:
    import magic
except ImportError:
    magic = None

from . import logger
from .i18n import _
from ._utils import random_string, guess_type


def get_date_last_pleroma_post(self):
    """Gathers last post from the user in Pleroma and returns the date
    of creation.

    :returns: Date of last Pleroma post in '%Y-%m-%dT%H:%M:%SZ' format
    """
    pleroma_posts_url = (
        f"{self.pleroma_base_url}/api/v1/accounts/"
        f"{self.pleroma_username}/statuses"
    )
    response = requests.get(pleroma_posts_url, headers=self.header_pleroma)
    if not response.ok:
        response.raise_for_status()
    posts = json.loads(response.text)
    self.posts = posts
    if posts:
        date_pleroma = posts[0]["created_at"]
    else:
        self.posts = "none_found"
        logger.warning(
            _("No posts were found in the target Fediverse account")
        )
        if self.first_time:
            date_pleroma = self.force_date()
        else:
            date_pleroma = datetime.strftime(
                datetime.now() - timedelta(days=2), "%Y-%m-%dT%H:%M:%SZ"
            )

    return date_pleroma


def post_pleroma(self, tweet: tuple, poll: dict, sensitive: bool) -> str:
    """Post the given text to the Pleroma instance associated with the
    User object

    :param tweet: Tuple containing tweet_id, tweet_text. The ID will be used to
    link to the Twitter status if 'signature' is True and to find related media
    tweet_text is the literal text to use when creating the post.
    :type tweet: tuple
    :param poll: dict of poll if attached to tweet
    :type poll: dict
    :param sensitive: if tweet is possibly sensitive or not
    :type sensitive: bool
    :returns: id of post
    :rtype: str
    """
    # TODO: transform twitter links to nitter links, if self.nitter
    #  'true' in resolved shortened urls
    pleroma_post_url = f"{self.pleroma_base_url}/api/v1/statuses"
    pleroma_media_url = f"{self.pleroma_base_url}/api/v1/media"

    tweet_id = tweet[0]
    tweet_text = tweet[1]
    tweet_folder = os.path.join(self.tweets_temp_path, tweet_id)
    media_files = os.listdir(tweet_folder)
    media_ids = []
    if self.media_upload:
        for file in media_files:
            media_file = open(os.path.join(tweet_folder, file), "rb")
            file_size = os.stat(os.path.join(tweet_folder, file)).st_size
            mime_type = guess_type(os.path.join(tweet_folder, file))
            timestamp = str(datetime.now().timestamp())
            file_name = (
                f"pleromapyupload_"
                f"{timestamp}"
                f"_"
                f"{random_string(10)}"
                f"{mimetypes.guess_extension(mime_type)}"
            )
            file_description = (file_name, media_file, mime_type)
            files = {"file": file_description}
            response = requests.post(
                pleroma_media_url, headers=self.header_pleroma, files=files
            )
            try:
                if not response.ok:
                    response.raise_for_status()
            except requests.exceptions.HTTPError:
                if response.status_code == 413:
                    size_msg = _(
                        "Exception occurred"
                        "\nMedia size too large:"
                        "\nFilename: {file}"
                        "\nSize: {size}MB"
                        "\nConsider increasing the attachment"
                        "\n size limit of your instance"
                    ).format(file=file, size=round(file_size / 1048576, 2))
                    logger.error(size_msg)
                    pass
                else:
                    response.raise_for_status()
            try:
                media_ids.append(json.loads(response.text)["id"])
            except (KeyError, JSONDecodeError):
                logger.warning(
                    _("Error uploading media:\t{}").format(str(response.text))
                )
                pass

    if self.signature:
        signature = f"\n\n 🐦🔗: {self.twitter_url}/status/{tweet_id}"
        tweet_text = f"{tweet_text} {signature}"

    # config setting override tweet attr
    if hasattr(self, "sensitive"):
        sensitive = self.sensitive

    data = {
        "status": tweet_text,
        "sensitive": str(sensitive).lower(),
        "visibility": self.visibility,
        "media_ids[]": media_ids,
    }

    if poll:
        data.update(
            {
                "poll[options][]": poll["options"],
                "poll[expires_in]": poll["expires_in"],
            }
        )

    if hasattr(self, "rich_text"):
        if self.rich_text:
            data.update({"content_type": self.content_type})
    response = requests.post(
        pleroma_post_url, data, headers=self.header_pleroma
    )
    if not response.ok:
        response.raise_for_status()
    logger.info(_("Post in Pleroma:\t{}").format(str(response)))
    post_id = json.loads(response.text)["id"]
    return post_id
