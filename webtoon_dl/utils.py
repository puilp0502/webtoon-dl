import re


def sanitize_filename(filename):
    """ Make filename safe to use in filesystems. """
    invalid = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid:
        filename = filename.replace(char, ' ')
    return filename.strip()


def parse_extension(uri):
    """ Parse the extension of URI. """
    patt = re.compile(r'(\.\w+)')
    return re.findall(patt, uri)[-1]
