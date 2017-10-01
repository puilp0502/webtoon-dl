import re
import time
import os

import requests


def sanitize_name(filename):
    invalid = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid:
        filename = filename.replace(char, ' ')
    return filename


def parse_extension(url):
    patt = re.compile(r'(\.\w+)')
    return re.findall(patt, url)[-1]


def download_file(url, foldername, referer, filename=None):
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    filename = os.path.basename(url) if filename is None else filename
    headers = {'Referer': referer}
    req = requests.get(url, headers=headers)
    with open(foldername + "/" + filename, "wb") as image:
        for chunk in req.iter_content(128):
            image.write(chunk)


def parse_img(src):
    patt = re.compile(
        r'(http://imgcomic.naver.net/webtoon/\d+/\d+/.+?\.(?:jpg|png|gif|bmp|JPG|PNG|GIF|BMP))')
    img_list = re.findall(patt, src)
    # print(img_list)
    return img_list


def readhtml(url):
    req = requests.get(url, allow_redirects=False)
    if req.status_code == 302:
        raise ConnectionRefusedError("Destination Moved")
    req.encoding = 'utf-8'
    return req.text


def main():
    page_url = input("Input url:")
    start = input("Start[1]:")
    if start == "":
        start = 1
    else:
        start = int(start)

    end = input("End[unlimited]:")
    if end == "":
        end = -1
    else:
        end = int(end)

    patt = re.compile(r"titleId=(\d+)")
    titleId = re.findall(patt, page_url)[0]
    print("Title Id: %s" % titleId)
    base_url = "http://comic.naver.com/webtoon/detail.nhn?titleId=" + titleId + "&no="
    print("Base URL: %s" % base_url)
    episode = start

    # Metadata Parsing
    first_episode = readhtml(base_url + '1')
    author_id = re.findall(r'<span class="wrt_nm">(.+?)</span>',
                           first_episode)[0].replace('/', '&').strip()
    comic_name = re.findall(r'<h2>(.+?)<span class="wrt_nm">',
                            first_episode)[0].replace('/', ' ').strip()
    print("Downloading " + author_id + "'s " + comic_name)

    while True:
        try:
            if end > 0:
                if episode > end:
                    exit()
            detail_url = base_url + str(episode)
            html_data = readhtml(detail_url)

            episode_name = re.findall(r'<h3>(.+?)</h3>', html_data)[0]
            print('Downloading %s' % episode_name)
            episode_name = sanitize_name(episode_name)

            imglist = parse_img(html_data)
            num = 1
            length = len(imglist)
            for image_url in imglist:
                print("    ", num)
                ext = parse_extension(image_url)
                path = author_id + "/" + comic_name + "/" + episode_name
                download_file(image_url, path, detail_url,
                              filename=str(num) + ext)
                num += 1
        except ConnectionRefusedError:
            print("\nEnd of comic")
            break
        except KeyboardInterrupt:
            print("\n\n-----Aborted!-----\n")
            break
        episode += 1


if __name__ == "__main__":
    main()
