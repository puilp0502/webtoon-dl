import html
import re

import requests

from webtoon_dl.providers.exceptions import EndOfComic
from webtoon_dl.utils import sanitize_filename


_image_list_pattern = re.compile(
    r'(https?://(imgcomic.naver.net|image-comic.pstatic.net)/webtoon/\d+/\d+/.+?\.(?:jpg|png|gif|bmp|JPG|PNG|GIF|BMP))')
_next_episode_pattern = re.compile(
    r"nclk_v2\(.+'con\.next'.?\);return checkServiceCode\('remoteCtr','.+?','(\d+)'")
_episode_name_pattern = re.compile(r'<h3>(.+?)</h3>')
_base_url = ""
_title_id = 0


def initialize(url):
    global _base_url
    _title_id = re.findall(r"titleId=(\d+)", url)[0]
    _base_url = "http://comic.naver.com/webtoon/detail.nhn?titleId=" + _title_id + "&no="


def get_image_list(src):
    """
    Get image list from given source.

    :src:
        A HTML source.
    """
    img_list = map(lambda m: m[0], re.findall(_image_list_pattern, src))
    return img_list


def get_next_episode_url(src):
    """
    Return next episode's url from given source src.

    Raises EndOfComic exception if next comic is not found.

    :src:
        A HTML source.
    """
    try:
        episode = re.findall(_next_episode_pattern, src)[0]
        return _base_url + episode
    except IndexError:
        raise EndOfComic


def get_episode_name(src):
    """
    Get episode name from given source.

    :src:
        A HTML source.
    """
    name = re.findall(_episode_name_pattern, src)[0]
    return html.unescape(name)


def get_dirname(src):
    """
    Get directory name to store comics.

    It will be called with the first episode to download,
    and will not be called again.

    Returned path must be sanitized using sanitize_filename.

    :src:
        A HTML source.
    """

    author_id = sanitize_filename(re.findall(
        r'<span class="wrt_nm">(.+?)</span>', src)[0]
        .replace('/', '&')).strip()
    comic_name = sanitize_filename(re.findall(
        r'<h2>(.+?)<span class="wrt_nm">', src)[0]).strip()
    return author_id + '/' + comic_name + '/'


def build_header(src, episode_url):
    """
    Build header.
    """
    return {'Referer': episode_url}
