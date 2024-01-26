import requests
from bs4 import BeautifulSoup  # 用于代替正则式 取源码中相应标签中的内容
import os
from rich.progress import track as tqdm
from concurrent.futures import ThreadPoolExecutor, wait
import time
from PIL import Image

class Editer(object):
    def __init__(self, comic_name, root_path = './', url_prev='site'):
        self.comic_name = comic_name
        self.root_path = root_path
        self.url_prev = url_prev
        self.comic_msg_url = f"https://api.copymanga.{url_prev}/api/v3/comic2/{comic_name}"
        self.comic_url_api = 'https://api.copymanga.{}/api/v3/comic/{}/group/{}/chapters?limit=500&offset=0&platform=3'
        self.chap_url_api = 'https://api.copymanga.{}/api/v3/comic/{}/chapter2/{}?platform=3'
        
        
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47', 'platform': '1'}

        self.max_thread_num = 16
        self.pool = ThreadPoolExecutor(self.max_thread_num)
        self.buffer_map = {}

    def get_comic_msg(self, is_gui=False, signal=None, editline=None):
        req = requests.get(self.comic_msg_url, headers=self.header).json()
        req = req['results']
        self.comic_title = req['comic']['name']
        self.comic_author = req['comic']['author'][0]['name']
        self.cover_url = req['comic']['cover']
        cls_dict = req['groups']
        self.cls_dict = {}
        for key in cls_dict.keys():
            self.cls_dict[cls_dict[key]['name']] = cls_dict[key]['path_word']
        if len(cls_dict.keys())==1:
            self.url_cls = list(self.cls_dict.values())[0]
        elif len(cls_dict.keys())>1:
            choise_name = self.get_choise(list(self.cls_dict.keys()), is_gui, signal, editline)
            self.url_cls = self.cls_dict[choise_name]
        self.comic_url = self.comic_url_api.format(self.url_prev, self.comic_name, self.url_cls)

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
        img_url = self.chap_url_api.format(self.url_prev, self.comic_name, uuid)
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

    def get_cover(self, chap_name, is_gui=False, signal=None):
        chap_path = os.path.join(self.comic_path, chap_name)
        imgfile = os.path.join(chap_path, '001.jpg')
        img = Image.open(imgfile)
        img_w, img_h = img.size
        signal_msg = (imgfile, img_h, img_w)
        if is_gui:
            signal.emit(signal_msg)

    def get_choise(self, choise_list, is_gui=False, signal=None, editline=None):
        if is_gui:
            error_msg = '漫画有多个部分， 请下拉选择框选择想下载的部分' 
            editline.addItems(choise_list)
            editline.setCurrentIndex(0)
            print(error_msg)
            signal.emit('hang')
            time.sleep(1)
            while not editline.isHidden():
                time.sleep(1)
            choise = editline.text()
            editline.clear()
        else:
            error_msg = '漫画有多个部分， 请输入想下载的部分的序号' 
            print(error_msg)
            for choise_no, choise in enumerate(choise_list):
                print(f'[{str(choise_no+1)}]', choise)
            choise_no = input('请输入序号:')
            choise_no = int(choise_no)-1
            choise = choise_list[choise_no]
        return choise
        

if __name__=='__main__':
    comic_name = 'yaoyeluying' 
    # comic_name = 'zgmsbywt' 
    downloader = Editer(comic_name=comic_name)
    for i in range(0, 3):
        chap_name = downloader.chap_name_list[i]
        chap_uuid = downloader.chap_uuid_list[i]
        downloader.download_single_chap(chap_name, chap_uuid)