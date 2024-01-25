import requests
from bs4 import BeautifulSoup  # 用于代替正则式 取源码中相应标签中的内容
import os
from rich.progress import track as tqdm
import threading
from concurrent.futures import ThreadPoolExecutor, wait
import time
import re

class Editer(object):
    def __init__(self, comic_name, root_path = './'):
        self.comic_name = comic_name
        self.root_path = root_path
        self.comic_main_page = 'https://www.copymanga.site/comic/{}'.format(comic_name)
        self.comic_url_api = 'https://api.copymanga.org/api/v3/comic/{}/group/default/chapters?limit=500&offset=0&platform=3'
        self.chap_url_api = 'https://api.copymanga.org/api/v3/comic/{}/chapter2/{}?platform=3'
        self.comic_url = self.comic_url_api.format(comic_name)

        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47', 'platform': '1'}

        self.max_thread_num = 16
        self.pool = ThreadPoolExecutor(self.max_thread_num)
        self.buffer_map = {}

    def get_comic_msg(self):
        req = requests.get(self.comic_main_page, headers=self.header)
        bf = BeautifulSoup(req.text, 'html.parser')
        self.comic_title = bf.find('h6').get('title')
        self.comic_author = bf.find('a', {'href': re.compile(r'^/author.*')}).text
        self.cover_url =  bf.find('img', {'class':'lazyload'}).get('data-src')
        
    def get_comic_chaps(self):
        req = requests.get(self.comic_url, headers=self.header)
        comic_urls = req.json()['results']['list']
        chap_name_list = []
        chap_uuid_list = []
        for comic_url in comic_urls:
            chap_name_list.append(comic_url['name'])
            chap_uuid_list.append(comic_url['uuid'])
        self.chap_name_list = chap_name_list
        self.chap_uuid_list = chap_uuid_list
        self.comic_path = os.path.join(self.root_path, self.comic_title)
        return self.chap_name_list, self.chap_uuid_list

    def get_image(self, is_gui=False, signal=None):
        self.pre_request_img()
        img_path = self.img_path
        if is_gui:
            len_iter = len(self.img_url_map.items())
            signal.emit('start')
            for i, (img_url, img_name) in enumerate(self.img_url_map.items()):
                content = self.get_html_img(img_url, is_buffer=True)
                with open(img_path+f'/{img_name}.jpg', 'wb') as f:
                    f.write(content) #写入二进制内容 
                signal.emit(int(100*(i+1)/len_iter))
            
    
    def download_single_chap(self, chap_name, uuid, multithread=True, is_gui=False, signal=None):
        os.makedirs(self.comic_path, exist_ok=True)
        print('正在下载'+chap_name)
        chap_path = os.path.join(self.comic_path, chap_name)
        os.makedirs(chap_path, exist_ok=True)
        img_url = self.chap_url_api.format(self.comic_name, uuid)
        req = requests.get(img_url, headers=self.header)
        img_urls = [url['url'] for url in req.json()['results']['chapter']['contents']]
        if multithread:
            for img_url in img_urls:
                self.pool.submit(self.prev_buffer, img_url)
        if is_gui:
            len_iter = len(img_urls)
            signal.emit('start') 
            for img_no, img_url in enumerate(img_urls):
                chap_name = os.path.join(chap_path, str(img_no+1).zfill(3)+'.jpg')
                self.download_img(img_url, chap_name, is_buffer=multithread)
                signal.emit(int(100*(img_no+1)/len_iter))
            signal.emit('end')
        else:
            for img_no, img_url in enumerate(tqdm(img_urls)):
                chap_name = os.path.join(chap_path, str(img_no+1).zfill(3)+'.jpg')
                self.download_img(img_url, chap_name, is_buffer=multithread)
                
    def download_img(self, img_url, file_name, is_buffer=False):
        if is_buffer:
            while img_url not in self.buffer_map.keys():
                time.sleep(1)
            req = self.buffer_map[img_url]
        else:
            req = requests.get(img_url, headers=self.header).content
        with open(file_name, 'wb') as f:
            f.write(req)

    def prev_buffer(self, url):
        if url not in self.buffer_map.keys():
            req = requests.get(url, headers=self.header).content
            self.buffer_map[url] = req

if __name__=='__main__':
    comic_name = 'yaoyeluying' 
    # comic_name = 'zgmsbywt' 
    downloader = Editer(comic_name=comic_name)
    for i in range(0, 3):
        chap_name = downloader.chap_name_list[i]
        chap_uuid = downloader.chap_uuid_list[i]
        downloader.download_single_chap(chap_name, chap_uuid)