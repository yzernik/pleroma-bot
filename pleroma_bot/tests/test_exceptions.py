import logging
import os
import shutil
import sys
from unittest.mock import patch

import pytest
import requests

from test_user import UserTemplate
from conftest import get_config_users

from pleroma_bot import cli
from pleroma_bot.cli import User


def test_user_invalid_pleroma_base(mock_request):
    """
    Check that a missing pleroma_base_url raises a KeyError exception
    """
    with mock_request['mock'] as mock:
        config_users = get_config_users('config_nopleroma.yml')
        for user_item in config_users['user_dict']:
            with pytest.raises(KeyError) as error_info:
                User(user_item, config_users['config'], os.getcwd())
            exception_value = (
                "'No Pleroma URL defined in config! [pleroma_base_url]'"
            )
            assert str(error_info.value) == exception_value
    return mock


def test_user_missing_twitter_base(sample_users):
    """
    Check that a missing pleroma_base_url raises a KeyError exception
    """
    test_user = UserTemplate()
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            config_users = get_config_users('config_notwitter.yml')
            for user_item in config_users['user_dict']:
                user_obj = User(user_item, config_users['config'], os.getcwd())
                assert user_obj.twitter_base_url_v2 is not None
                assert user_obj.twitter_base_url is not None
                assert user_obj.twitter_base_url == test_user.twitter_base_url
                assert (
                    user_obj.twitter_base_url_v2 ==
                    test_user.twitter_base_url_v2
                )
        return mock


def test_user_nitter_global(sample_users):
    """
    Check that a missing pleroma_base_url raises a KeyError exception
    """
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            config_users = get_config_users('config_nitter_global.yml')
            for user_item in config_users['user_dict']:
                user_obj = User(user_item, config_users['config'], os.getcwd())
                nitter_url = f"https://nitter.net/{user_obj.twitter_username}"
                assert user_obj.twitter_url is not None
                assert user_obj.twitter_url == nitter_url
            config_users = get_config_users('config_nonitter.yml')
            # No global
            for user_item in config_users['user_dict']:
                user_obj = User(user_item, config_users['config'], os.getcwd())
                twitter_url = f"http://twitter.com/{user_obj.twitter_username}"
                assert user_obj.twitter_url == twitter_url
        return mock


def test_user_invalid_visibility(sample_users):
    """
    Check that an improper visibility value in the config raises a
    KeyError exception
    """
    with pytest.raises(KeyError) as error_info:
        for sample_user in sample_users:
            with sample_user['mock'] as mock:
                config_users = get_config_users('config_visibility.yml')
                for user_item in config_users['user_dict']:
                    user_obj = User(
                        user_item, config_users['config'], os.getcwd()
                    )
                    user_obj['mock'] = mock
    str_error = (
        "'Visibility not supported! Values allowed are: "
        "public, unlisted, private and direct'"
    )
    assert str(error_info.value) == str(str_error)


def test_user_invalid_max_tweets(sample_users):
    """
    Check that an improper max_tweets value in the config raises a
    ValueError exception
    """
    error_str = 'max_tweets must be between 10 and 100. max_tweets: 5'
    with pytest.raises(ValueError) as error_info:
        for sample_user in sample_users:
            with sample_user['mock'] as mock:
                config_users = get_config_users('config_max_tweets_global.yml')
                for user_item in config_users['user_dict']:
                    user_obj = User(
                        user_item, config_users['config'], os.getcwd()
                    )
                    start_time = user_obj.get_date_last_pleroma_post()
                    user_obj.get_tweets(start_time=start_time)

    assert str(error_info.value) == error_str
    with pytest.raises(ValueError):
        for sample_user in sample_users:
            with sample_user['mock'] as mock:
                config_users = get_config_users('config_max_tweets_user.yml')
                for user_item in config_users['user_dict']:
                    user_obj = User(
                        user_item, config_users['config'], os.getcwd()
                    )
                    start_time = user_obj.get_date_last_pleroma_post()
                    user_obj.get_tweets(start_time=start_time)
                user_obj['mock'] = mock
    assert str(error_info.value) == error_str
    return mock


def test_get_date_last_pleroma_post_exception(sample_users, mock_request):
    with pytest.raises(requests.exceptions.HTTPError) as error_info:
        test_user = UserTemplate()

        for sample_user in sample_users:
            with sample_user['mock'] as mock:
                sample_user_obj = sample_user['user_obj']
                url_statuses = (
                    f"{test_user.pleroma_base_url}"
                    f"/api/v1/accounts/"
                    f"{sample_user_obj.pleroma_username}/statuses"
                )
                mock.get(
                    url_statuses,
                    json=mock_request['sample_data']['pleroma_statuses_pin'],
                    status_code=500
                )
                sample_user_obj.get_date_last_pleroma_post()

    exception_value = f"500 Server Error: None for url: {url_statuses}"
    assert str(error_info.value) == exception_value


def test_get_tweets_unknown_version(sample_users, mock_request):
    with pytest.raises(ValueError) as error_info:
        for sample_user in sample_users:
            with sample_user['mock'] as mock:
                sample_user_obj = sample_user['user_obj']
                sample_user_obj._get_tweets("nonsense")
    assert str(error_info.value) == 'API version not supported: nonsense'
    return mock


def test_post_pleroma_exception(sample_users, mock_request):
    test_user = UserTemplate()
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            tweets_folder = sample_user_obj.tweets_temp_path
            tweet_folder = os.path.join(tweets_folder, test_user.pinned)
            os.makedirs(tweet_folder, exist_ok=True)
            post_url = f"{test_user.pleroma_base_url}/api/v1/statuses"
            mock.post(post_url, status_code=500)
            with pytest.raises(requests.exceptions.HTTPError) as error_info:
                sample_user_obj.post_pleroma(
                    (test_user.pinned, ""), None, False
                )
            exception_value = f"500 Server Error: None for url: {post_url}"
            assert str(error_info.value) == exception_value
            os.rmdir(tweet_folder)


# TODO: Redo this test without using pinned_tweet_id
# def test__get_tweets_exception(sample_users, mock_request):
#     for sample_user in sample_users:
#         with sample_user['mock'] as mock:
#             sample_user_obj = sample_user['user_obj']
#             tweet_id_url = (
#                 f"{sample_user_obj.twitter_base_url}/statuses/"
#                 f"show.json?id={str(sample_user_obj.pinned_tweet_id)}"
#             )

#             mock.get(tweet_id_url, status_code=500)
#             with pytest.raises(requests.exceptions.HTTPError) as error_info:
#                 sample_user_obj._get_tweets(
#                     "v1.1", sample_user_obj.pinned_tweet_id
#                 )
#             exception_value = \
#             f"500 Server Error: None for url: {tweet_id_url}"
#             assert str(error_info.value) == exception_value
#             tweets_url = (
#                 f"{sample_user_obj.twitter_base_url}"
#                 f"/statuses/user_timeline.json?screen_name="
#                 f"{sample_user_obj.twitter_username}"
#                 f"&count={str(sample_user_obj.max_tweets)}&include_rts=true"
#             )
#             mock.get(tweets_url, status_code=500)
#             with pytest.raises(requests.exceptions.HTTPError) as error_info:
#                 sample_user_obj._get_tweets("v1.1")
#             exception_value = f"500 Server Error: None for url: {tweets_url}"
#             assert str(error_info.value) == exception_value


def test__get_tweets_v2_exception(sample_users):
    test_user = UserTemplate()
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            tweets_url = (
                f"{test_user.twitter_base_url_v2}/users/by?"
                f"usernames={sample_user_obj.twitter_username}"
            )
            mock.get(tweets_url, status_code=500)
            start_time = sample_user_obj.get_date_last_pleroma_post()
            with pytest.raises(requests.exceptions.HTTPError) as error_info:
                sample_user_obj._get_tweets(
                    "v2", start_time=start_time
                )
            exception_value = f"500 Server Error: None for url: {tweets_url}"
            assert str(error_info.value) == exception_value


def test__get_twitter_info_exception(sample_users):
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            info_url = (
                f"{sample_user_obj.twitter_base_url}"
                f"/users/show.json?screen_name="
                f"{sample_user_obj.twitter_username}"
            )
            mock.get(info_url, status_code=500)
            with pytest.raises(requests.exceptions.HTTPError) as error_info:
                sample_user_obj._get_twitter_info()
            exception_value = f"500 Server Error: None for url: {info_url}"
            assert str(error_info.value) == exception_value


def test_main_oauth_exception(
        rootdir, global_mock, sample_users, mock_request, monkeypatch, caplog
):
    test_user = UserTemplate()
    with global_mock as g_mock:
        test_files_dir = os.path.join(rootdir, 'test_files')

        config_test = os.path.join(test_files_dir, 'config_multiple_users.yml')
        prev_config = os.path.join(os.getcwd(), 'config.yml')
        backup_config = os.path.join(os.getcwd(), 'config.yml.bak')
        if os.path.isfile(prev_config):
            shutil.copy(prev_config, backup_config)
        shutil.copy(config_test, prev_config)

        users_path = os.path.join(os.getcwd(), 'users')
        shutil.rmtree(users_path)

        g_mock.get(f"{test_user.twitter_base_url_v2}/users/2244994945"
                   f"/tweets",
                   json={},
                   status_code=200)

        monkeypatch.setattr('builtins.input', lambda: "2020-12-30")
        with patch.object(sys, 'argv', ['']):
            with caplog.at_level(logging.ERROR):
                assert cli.main() == 1
                err_msg = (
                    "Unable to retrieve tweets. Is the account protected? "
                    "If so, you need to provide the following OAuth 1.0a "
                    "fields in the user config:"
                )
                assert err_msg in caplog.text

        # Clean-up
        g_mock.get(f"{test_user.twitter_base_url_v2}/users/2244994945"
                   f"/tweets",
                   json=mock_request['sample_data']['tweets_v2'],
                   status_code=200)
        if os.path.isfile(backup_config):
            shutil.copy(backup_config, prev_config)
        for sample_user in sample_users:
            sample_user_obj = sample_user['user_obj']
            pinned_path = os.path.join(os.getcwd(),
                                       'users',
                                       sample_user_obj.twitter_username,
                                       'pinned_id.txt')
            pinned_pleroma = os.path.join(os.getcwd(),
                                          'users',
                                          sample_user_obj.twitter_username,
                                          'pinned_id_pleroma.txt')
            if os.path.isfile(pinned_path):
                os.remove(pinned_path)
            if os.path.isfile(pinned_pleroma):
                os.remove(pinned_pleroma)
    return g_mock


def test__get_instance_info_exception(sample_users):
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            info_url = (
                f"{sample_user_obj.pleroma_base_url}/api/v1/instance"
            )
            mock.get(info_url, status_code=500)
            with pytest.raises(requests.exceptions.HTTPError) as error_info:
                sample_user_obj._get_instance_info()
            exception_value = f"500 Server Error: None for url: {info_url}"
            assert str(error_info.value) == exception_value

            down_msg = "Instance under maintenance"
            mock.get(info_url, text=down_msg, status_code=200)
            with pytest.raises(ValueError) as error_info:
                sample_user_obj._get_instance_info()
            exception_value = (
                f"Instance response was not understood {down_msg}"
            )
            assert str(error_info.value) == exception_value


def test__download_media_exception(sample_users, caplog):
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            media_url = "https://mymock.media/img.jpg"
            mock.get(media_url, status_code=500)
            media = [{'url': media_url, 'type': 'image'}]
            tweet = None
            with pytest.raises(requests.exceptions.HTTPError) as error_info:
                sample_user_obj._download_media(media, tweet)
            exception_value = f"500 Server Error: None for url: {media_url}"
            assert str(error_info.value) == exception_value
            mock.get(media_url, status_code=404)
            tweet = None
            with caplog.at_level(logging.WARNING):
                sample_user_obj._download_media(media, tweet)
            warn_msg1 = "Media not found (404)"
            warn_msg2 = "Ignoring attachment and continuing..."
            assert warn_msg1 in caplog.text
            assert warn_msg2 in caplog.text


def test__expand_urls(sample_users, mock_request):
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            fake_url = "https://cutt.ly/xg3TuY0"
            mock.head(fake_url, status_code=500)
            tweet = mock_request['sample_data']['pinned_tweet']['data']
            with pytest.raises(requests.exceptions.HTTPError) as error_info:
                sample_user_obj._expand_urls(tweet)
            exception_value = f"500 Server Error: None for url: {fake_url}"
            assert str(error_info.value) == exception_value
