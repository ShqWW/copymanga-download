import zipfile
import os
import shutil
from utils import *
from PIL import Image
import numpy as np

class Editer(object):
    def __init__(self, title, author, chap_list, comic_root, out_root, delete_comic=False):

        self.title = self.get_epub_title(title, chap_list)
        self.author = author
        self.chap_list = chap_list
        self.comic_root = comic_root
        self.out_root = out_root

        self.img_list = []
        self.chap_first_imgs = []
        self.delete_comic = delete_comic

    def pack_img(self):

        self.epub_path = os.path.join(self.out_root, 'tmp')
        self.epub_oebps_path = os.path.join(self.out_root, 'tmp/OEBPS')
        self.epub_img_path = os.path.join(self.out_root, 'tmp/OEBPS/Images')
        self.epub_text_path = os.path.join(self.out_root, 'tmp/OEBPS/Text')
        os.makedirs(self.epub_path, exist_ok=True)
        os.makedirs(self.epub_oebps_path, exist_ok=True)
        os.makedirs(self.epub_img_path, exist_ok=True)
        os.makedirs(self.epub_text_path, exist_ok=True)
        
        print('正在打包处理图片......')
        for chap_no, chap in enumerate(self.chap_list):
            img_path = os.path.join(self.comic_root, chap)
            imgs = os.listdir(img_path)
            img_no = 0
            self.chap_first_imgs.append(str(chap_no+1).zfill(3) + '_' + str(0).zfill(4) + '.jpg')
            for img_no, img in enumerate(imgs):
                img_old_path = os.path.join(img_path, img)
                img_new = str(chap_no + 1).zfill(3) + '_' + str(img_no).zfill(4) + '.jpg'
                img_epub_path = os.path.join(self.epub_img_path, img_new)
                shutil.copyfile(img_old_path, img_epub_path)
                self.img_list.append(img_new)

    def get_epub_title(self, title, chap_list):
        if len(chap_list)==1:
            title = title + '-' + chap_list[0]
        else:
            title = title + '-' + chap_list[0] + '-' + chap_list[-1]
        return title

    def typesetting(self):
        print('正在生成排版......')
        for img in self.img_list:
            text_file = os.path.join(self.epub_text_path, img.replace('.jpg', '.xhtml'))
            text_htmls = get_xhtml(img)
            with open(text_file, 'w+', encoding='utf-8') as f:
                f.writelines(text_htmls)


        print('正在生成元数据......')


        #封面
        cover_path = os.path.join(self.epub_img_path, '000_0000.jpg')
        shutil.copyfile(os.path.join(self.comic_root, 'cover.jpg'), cover_path)
        textfile = os.path.join(self.epub_text_path, 'cover.xhtml')
        # img = cv2.imread(cover_path)
        img = Image.open(cover_path)
        img = np.array(img)
        img_htmls = get_cover_html(img.shape[1], img.shape[0])
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(img_htmls)


        #内容页
        content_htmls = get_content_html(self.title, self.author, self.img_list)
        textfile = os.path.join(self.epub_oebps_path, 'content.opf')
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(content_htmls)

        #目录
        toc_htmls = get_toc_html(self.title, self.chap_list, self.chap_first_imgs)
        textfile = os.path.join(self.epub_oebps_path, 'toc.ncx')
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(toc_htmls)

        #get epub_head
        mimetype = 'application/epub+zip'
        mimetypefile = os.path.join(self.epub_path, 'mimetype')
        with open(mimetypefile, 'w+', encoding='utf-8') as f:
            f.write(mimetype)
        metainf_folder = os.path.join(self.epub_path, 'META-INF')
        os.makedirs(metainf_folder, exist_ok=True)
        container = metainf_folder + '/container.xml'
        container_htmls = get_container_html()
        with open(container, 'w+', encoding='utf-8') as f:
            f.writelines(container_htmls)
    
    def get_epub(self):
        print('正在打包EPUB......')
        epub_file = os.path.join(self.out_root, self.title + '.epub')
        with zipfile.ZipFile(epub_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, dirnames, filenames in os.walk(self.epub_path):
                fpath = dirpath.replace(self.epub_path,'')
                fpath = fpath and fpath + os.sep or ''
                for filename in filenames:
                    zf.write(os.path.join(dirpath, filename), fpath+filename)
        shutil.rmtree(self.epub_path)
        if self.delete_comic:
            shutil.rmtree(self.comic_root)
        print('EPUB生成成功, 路径【{}】'.format(epub_file))