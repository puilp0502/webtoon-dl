"""
Webtoon providers.

A provider is module containing functions to parse webtoons.
A provider implements:
    get_image_list(src): Get image list from given source.
    get_next_episode_url(src): Get next episode's url from given source.
    get_episode_name(src): Get episode's name from given source.

A mapping is a list of (pattern, module).
If the `pattern` is found in url, the `module` will be used as a provider.
:pattern:
    Either `str` or callable.
    If pattern is callable, it should return boolean value.
:module:
    module name of the provider, relative to the provider package.
    Prepending dots need not be attached.
"""

mapping = [
    ('comic.naver.com', "naver"),
]
