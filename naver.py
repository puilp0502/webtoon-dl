import requests
import re
import time, os

def download_file(url, foldername, referer):
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    filename = os.path.basename(url)
    headers = {'Referer': referer}
    req = requests.get(url, headers = headers)
    with open(foldername+"\\"+filename, "wb") as image:
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
patt = re.compile(r"titleId=(\d+)")
titleId = re.findall(patt, page_url)[0]
print("Title Id: %s"%titleId)
base_url = "http://comic.naver.com/webtoon/detail.nhn?titleId="+titleId+"&no="
print("Base URL: %s"%base_url)
episode = 1
while True:
    try:
        detail_url = base_url+str(episode)
        print("Episode %d"%episode)
        #print("URL: %s"%detail_url)
        for image_url in parse_img(readhtml(detail_url)):
            print("  Downloading file %s"%os.path.basename(image_url))
            download_file(image_url, str(titleId)+"\\"+str(episode),detail_url)
    except ConnectionRefusedError:
        print("\nEnd of comic")
        break
    except KeyboardInterrupt:
        print("\n\n-----Aborted!-----\n")
        break
    episode += 1
