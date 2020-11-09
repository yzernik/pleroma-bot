import os
import shutil
from datetime import datetime, timedelta
import urllib.parse

from test_user import TestUser
from conftest import get_config_users

from pleroma_bot._utils import random_string
from pleroma_bot._utils import guess_type


def test_random_string():
    """
    Check that random string returns a string of the desired length
    """
    random_10 = random_string(10)
    assert len(random_10) == 10


def test_user_replace_vars_in_str(sample_users):
    """
    Check that replace_vars_in_str replaces the var_name with the var_value
    correctly
    """
    test_user = TestUser()
    for sample_user in sample_users:
        user_obj = sample_user['user_obj']
        replace = user_obj.replace_vars_in_str(test_user.replace_str)
        assert replace == sample_user['user_obj'].twitter_url


def test_user_attrs(sample_users):
    """
    Check that test user matches sample data fed by the mock
    """
    test_user = TestUser()
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            pleroma_date = sample_user_obj.get_date_last_pleroma_post()
            pinned = sample_user_obj.pinned_tweet_id
            sample_user_obj.get_date_last_pleroma_post()
            assert pinned == test_user.pinned
            assert pleroma_date == test_user.pleroma_date
            assert sample_user_obj.twitter_base_url == \
                   test_user.twitter_base_url
            assert sample_user_obj.twitter_token == test_user.twitter_token
            assert sample_user_obj.pleroma_token == test_user.pleroma_token
            assert (
                sample_user_obj.twitter_base_url_v2 ==
                test_user.twitter_base_url_v2
            )
            assert sample_user_obj.nitter == test_user.nitter
        return mock


def test_check_pinned_tweet(sample_users, mock_request):
    """
    Needs to test the following Previous - Current pin statuses:
        Pinned -> Pinned (same pin)
        Pinned -> Pinned (diff pin)
        Pinned -> None
        None   -> None
        None   -> Pinned
    """
    test_user = TestUser()
    # Pinned -> Pinned
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            pinned = sample_user_obj.pinned_tweet_id
            assert pinned == test_user.pinned
            mock.get(f"{test_user.twitter_base_url_v2}/tweets/{pinned}"
                     f"?poll.fields=duration_minutes%2Cend_datetime%2Cid%2C"
                     f"options%2Cvoting_status&media.fields=duration_ms%2C"
                     f"height%2Cmedia_key%2Cpreview_image_url%2Ctype%2Curl%2C"
                     f"width%2Cpublic_metrics&expansions=attachments.poll_ids"
                     f"%2Cattachments.media_keys%2Cauthor_id%2C"
                     f"entities.mentions.username%2Cgeo.place_id%2C"
                     f"in_reply_to_user_id%2Creferenced_tweets.id%2C"
                     f"referenced_tweets.id.author_id&tweet.fields=attachments"
                     f"%2Cauthor_id%2Ccontext_annotations%2Cconversation_id%2"
                     f"Ccreated_at%2Centities%2Cgeo%2Cid%2Cin_reply_to_user_id"
                     f"%2Clang%2Cpublic_metrics%2Cpossibly_sensitive%2C"
                     f"referenced_tweets%2Csource%2Ctext%2Cwithheld",
                     json=mock_request['sample_data']['pinned_tweet'],
                     status_code=200)
            mock.get(f"{test_user.twitter_base_url_v2}/tweets?ids={pinned}"
                     f"&expansions=attachments.poll_ids"
                     f"&poll.fields=duration_minutes%2Coptions",
                     json=mock_request['sample_data']['poll'],
                     status_code=200)
            pinned_file = os.path.join(
                os.getcwd(),
                'users',
                sample_user_obj.twitter_username,
                'pinned_id.txt'
            )
            with open(pinned_file, "w") as f:
                f.write(test_user.pinned + "\n")
            sample_user_obj.check_pinned()
            pinned_path = os.path.join(os.getcwd(),
                                       'users',
                                       sample_user_obj.twitter_username,
                                       'pinned_id.txt')
            pinned_pleroma = os.path.join(os.getcwd(),
                                          'users',
                                          sample_user_obj.twitter_username,
                                          'pinned_id_pleroma.txt')
            with open(pinned_path, 'r', encoding='utf8') as f:
                assert f.readline().rstrip() == test_user.pinned

            # Pinned -> Pinned (different ID)
            pinned_url = (
                f"{test_user.twitter_base_url_v2}/users/by/username/"
                f"{sample_user_obj.twitter_username}"
            )
            mock.get(pinned_url,
                     json=mock_request['sample_data']['pinned_2'],
                     status_code=200)
            new_pin_id = sample_user_obj._get_pinned_tweet_id()
            sample_user_obj.pinned_tweet_id = new_pin_id
            pinned = sample_user_obj.pinned_tweet_id
            mock.get(f"{test_user.twitter_base_url_v2}/tweets/{pinned}"
                     f"?poll.fields=duration_minutes%2Cend_datetime%2Cid%2C"
                     f"options%2Cvoting_status&media.fields=duration_ms%2C"
                     f"height%2Cmedia_key%2Cpreview_image_url%2Ctype%2Curl%2C"
                     f"width%2Cpublic_metrics&expansions=attachments.poll_ids"
                     f"%2Cattachments.media_keys%2Cauthor_id%2C"
                     f"entities.mentions.username%2Cgeo.place_id%2C"
                     f"in_reply_to_user_id%2Creferenced_tweets.id%2C"
                     f"referenced_tweets.id.author_id&tweet.fields=attachments"
                     f"%2Cauthor_id%2Ccontext_annotations%2Cconversation_id%2"
                     f"Ccreated_at%2Centities%2Cgeo%2Cid%2Cin_reply_to_user_id"
                     f"%2Clang%2Cpublic_metrics%2Cpossibly_sensitive%2C"
                     f"referenced_tweets%2Csource%2Ctext%2Cwithheld",
                     json=mock_request['sample_data']['pinned_tweet_2'],
                     status_code=200)
            mock.get(f"{test_user.twitter_base_url_v2}/tweets?ids={pinned}"
                     f"&expansions=attachments.poll_ids"
                     f"&poll.fields=duration_minutes%2Coptions",
                     json=mock_request['sample_data']['poll_2'],
                     status_code=200)
            sample_user_obj.check_pinned()
            with open(pinned_path, 'r', encoding='utf8') as f:
                assert f.readline().rstrip() == test_user.pinned_2
            id_pleroma = test_user.pleroma_pinned
            with open(pinned_pleroma, 'r', encoding='utf8') as f:
                assert f.readline().rstrip() == id_pleroma

            # Pinned -> None
            mock.get(f"{test_user.twitter_base_url_v2}/users/by/username/"
                     f"{sample_user_obj.twitter_username}",
                     json=mock_request['sample_data']['no_pinned'],
                     status_code=200)
            new_pin_id = sample_user_obj._get_pinned_tweet_id()
            sample_user_obj.pinned_tweet_id = new_pin_id
            sample_user_obj.check_pinned()
            with open(pinned_path, 'r', encoding='utf8') as f:
                assert f.readline().rstrip() == ''
            with open(pinned_pleroma, 'r', encoding='utf8') as f:
                assert f.readline().rstrip() == ''
            history = mock.request_history
            unpin_url = (
                f"{sample_user_obj.pleroma_base_url}"
                f"/api/v1/statuses/{test_user.pleroma_pinned}/unpin"
            )
            assert unpin_url == history[-1].url

            # None -> None
            sample_user_obj.check_pinned()
            with open(pinned_path, 'r', encoding='utf8') as f:
                assert f.readline().rstrip() == ''
            with open(pinned_pleroma, 'r', encoding='utf8') as f:
                assert f.readline().rstrip() == ''

            # None -> Pinned
            pinned_url = (
                f"{test_user.twitter_base_url_v2}/users/by/username/"
                f"{sample_user_obj.twitter_username}"
            )
            mock.get(pinned_url,
                     json=mock_request['sample_data']['pinned'],
                     status_code=200)
            new_pin_id = sample_user_obj._get_pinned_tweet_id()
            sample_user_obj.pinned_tweet_id = new_pin_id
            pinned = sample_user_obj.pinned_tweet_id
            mock.get(f"{test_user.twitter_base_url_v2}/tweets/{pinned}"
                     f"?poll.fields=duration_minutes%2Cend_datetime%2Cid%2C"
                     f"options%2Cvoting_status&media.fields=duration_ms%2C"
                     f"height%2Cmedia_key%2Cpreview_image_url%2Ctype%2Curl%2C"
                     f"width%2Cpublic_metrics&expansions=attachments.poll_ids"
                     f"%2Cattachments.media_keys%2Cauthor_id%2C"
                     f"entities.mentions.username%2Cgeo.place_id%2C"
                     f"in_reply_to_user_id%2Creferenced_tweets.id%2C"
                     f"referenced_tweets.id.author_id&tweet.fields=attachments"
                     f"%2Cauthor_id%2Ccontext_annotations%2Cconversation_id%2"
                     f"Ccreated_at%2Centities%2Cgeo%2Cid%2Cin_reply_to_user_id"
                     f"%2Clang%2Cpublic_metrics%2Cpossibly_sensitive%2C"
                     f"referenced_tweets%2Csource%2Ctext%2Cwithheld",
                     json=mock_request['sample_data']['pinned_tweet'],
                     status_code=200)
            mock.get(f"{test_user.twitter_base_url_v2}/tweets?ids={pinned}"
                     f"&expansions=attachments.poll_ids"
                     f"&poll.fields=duration_minutes%2Coptions",
                     json=mock_request['sample_data']['poll'],
                     status_code=200)
            sample_user_obj.check_pinned()
            with open(pinned_path, 'r', encoding='utf8') as f:
                assert f.readline().rstrip() == test_user.pinned
            id_pleroma = test_user.pleroma_pinned
            with open(pinned_pleroma, 'r', encoding='utf8') as f:
                assert f.readline().rstrip() == id_pleroma
            os.remove(pinned_path)
            os.remove(pinned_pleroma)


def test_get_date_last_pleroma_post(sample_users):
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            date = sample_user_obj.get_date_last_pleroma_post()
            ts = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
    return ts, mock


def test_get_date_last_pleroma_post_no_posts(sample_users):
    test_user = TestUser()
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']

            url_statuses = (
                f"{test_user.pleroma_base_url}"
                f"/api/v1/accounts/"
                f"{sample_user_obj.pleroma_username}/statuses"
            )
            mock.get(url_statuses, json={}, status_code=200)

            date_sample = sample_user_obj.get_date_last_pleroma_post()
            ts = datetime.strptime(str(date_sample), "%Y-%m-%d %H:%M:%S")
            date_pleroma = datetime.strftime(
                datetime.now() - timedelta(days=2), "%Y-%m-%d %H:%M:%S"
            )
            assert date_sample == date_pleroma
    return ts


def test_guess_type(rootdir):
    """
    Test the guess_type functiona against different MIME types
    """
    test_files_dir = os.path.join(rootdir, 'test_files')
    sample_data_dir = os.path.join(test_files_dir, 'sample_data')
    media_dir = os.path.join(sample_data_dir, 'media')
    png = os.path.join(media_dir, 'image.png')
    svg = os.path.join(media_dir, 'image.svg')
    mp4 = os.path.join(media_dir, 'video.mp4')
    gif = os.path.join(media_dir, "animated_gif.gif")
    assert 'image/png' == guess_type(png)
    assert 'image/svg+xml' == guess_type(svg)
    assert 'video/mp4' == guess_type(mp4)
    assert 'image/gif' == guess_type(gif)


def test_get_twitter_info(mock_request, sample_users, rootdir):
    """
    Check that _get_twitter_info retrieves the correct profile image and banner
    URLs
    """
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            twitter_info = mock_request['sample_data']['twitter_info']
            banner_url = twitter_info['profile_banner_url']
            profile_pic_url = twitter_info['profile_image_url_https']

            sample_user_obj._get_twitter_info()

            p_banner_url = sample_user_obj.profile_banner_url
            p_image_url = sample_user_obj.profile_image_url
            assert banner_url == p_banner_url
            assert profile_pic_url == p_image_url
    return mock


def test_update_pleroma(mock_request, sample_users, rootdir):
    """
    Check that update_pleroma downloads the correct profile image and banner
    """
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            test_files_dir = os.path.join(rootdir, 'test_files')
            sample_data_dir = os.path.join(test_files_dir, 'sample_data')
            media_dir = os.path.join(sample_data_dir, 'media')

            banner = os.path.join(media_dir, 'banner.jpg')
            profile_banner = open(banner, 'rb')
            profile_banner_content = profile_banner.read()
            profile_banner.close()

            profile_pic = os.path.join(media_dir, 'default_profile_normal.png')
            profile_image = open(profile_pic, 'rb')
            profile_image_content = profile_image.read()
            profile_image.close()

            sample_user_obj.update_pleroma()

            t_profile_banner = open(sample_user_obj.header_path, 'rb')
            t_profile_banner_content = t_profile_banner.read()
            t_profile_banner.close()

            t_profile_image = open(sample_user_obj.avatar_path, 'rb')
            t_profile_image_content = t_profile_image.read()
            t_profile_image.close()
            assert t_profile_banner_content == profile_banner_content
            assert t_profile_image_content == profile_image_content
    return mock


def test_post_pleroma_media(rootdir, sample_users, mock_request):
    test_user = TestUser()
    for sample_user in sample_users:
        with sample_user['mock'] as mock:
            sample_user_obj = sample_user['user_obj']
            if sample_user_obj.media_upload:
                test_files_dir = os.path.join(rootdir, 'test_files')
                sample_data_dir = os.path.join(test_files_dir, 'sample_data')
                media_dir = os.path.join(sample_data_dir, 'media')
                png = os.path.join(media_dir, 'image.png')
                svg = os.path.join(media_dir, 'image.svg')
                mp4 = os.path.join(media_dir, 'video.mp4')
                gif = os.path.join(media_dir, "animated_gif.gif")
                tweet_folder = os.path.join(
                    sample_user_obj.tweets_temp_path, test_user.pinned
                )
                shutil.copy(png, tweet_folder)
                shutil.copy(svg, tweet_folder)
                shutil.copy(mp4, tweet_folder)
                shutil.copy(gif, tweet_folder)
                attach_number = len(os.listdir(tweet_folder))
                sample_user_obj.post_pleroma(test_user.pinned, "", None, False)

                history = mock.request_history
                post_url = (
                    f"{sample_user_obj.pleroma_base_url}/api/v1/statuses"
                )
                assert post_url == history[-1].url
                token_sample = sample_user_obj.header_pleroma['Authorization']
                config_users = get_config_users('config.yml')
                users = config_users['user_dict']
                for user in users:
                    if (
                        user['pleroma_username']
                        == sample_user_obj.pleroma_username
                    ):
                        token_config = user['pleroma_token']

                assert f"Bearer {token_config}" == token_sample
                assert token_sample == history[-1].headers['Authorization']
                mock_media = mock_request['sample_data']['pleroma_post_media']
                id_media = mock_media['id']
                assert id_media in history[-1].text
                dict_history = urllib.parse.parse_qs(history[-1].text)
                assert len(dict_history['media_ids[]']) == attach_number
                for media in dict_history['media_ids[]']:
                    assert media == id_media

                for media_file in os.listdir(tweet_folder):
                    os.remove(os.path.join(tweet_folder, media_file))
