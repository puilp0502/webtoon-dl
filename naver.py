import re
import time, os

import requests


def download_file(url, foldername, referer):
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    filename = os.path.basename(url)
    headers = {'Referer': referer}
    req = requests.get(url, headers = headers)
    #print(foldername+"/"+filename)
    with open(foldername+"/"+filename, "wb") as image:
        for chunk in req.iter_content(128):
            image.write(chunk)
    
def parse_img(src):
    patt = re.compile(r'(http://imgcomic.naver.net/webtoon/\d+/\d+/.+?\.(?:jpg|png|gif|bmp|JPG|PNG|GIF|BMP))')
    img_list = re.findall(patt, src)
    #print(img_list)
    return img_list

def readhtml(url):
    req = requests.get(url,allow_redirects=False)
    if req.status_code == 302: raise ConnectionRefusedError("Destination Moved")
    req.encoding = 'utf-8'
    return req.text

page_url = input("Input url:")
start=input("Start[1]:")
if start=="":
    start=1
else:
    start=int(start)

end=input("End[unlimited]:")
if end=="":
    end=-1
else:
    end=int(end)

patt = re.compile(r"titleId=(\d+)")
titleId = re.findall(patt, page_url)[0]
print("Title Id: %s"%titleId)
base_url = "http://comic.naver.com/webtoon/detail.nhn?titleId="+titleId+"&no="
print("Base URL: %s"%base_url)
episode = start
while True:
    try:
        if end>0:
            if episode>end:
                exit()
        detail_url = base_url+str(episode)
        print("Episode %d"%episode)
        #print("URL: %s"%detail_url)
        html_data = readhtml(detail_url)
        author_id = re.findall(r'<span class="wrt_nm">(.+?)</span>', html_data)[0].replace('/', '&').strip()
        comic_name= re.findall(r'<h2>(.+?)<span class="wrt_nm">', html_data)[0].replace('/', ' ').strip()

        print("Downloading "+author_id + "'s " + comic_name)
        imglist = parse_img(html_data)
        num = 1
        length = len(imglist)
        for image_url in imglist:
            print("    ", num)
            download_file(image_url, author_id+"/"+comic_name+"/"+str(episode),detail_url)
            num += 1
    except ConnectionRefusedError:
        print("\nEnd of comic")
        break
    except KeyboardInterrupt:
        print("\n\n-----Aborted!-----\n")
        break
    episode += 1
