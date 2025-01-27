from .Downloader import Downloader
from .Editer import Editer
from .utils import *

def query_chaps(comic_name, url, is_gui=False, hang_signal=None, edit_line_hang=None):
    print('未输入编号，将返回漫画目录信息......')
    editer = Downloader(comic_name=comic_name, root_path='./out', url=url, num_thread=1)
    print('*******************************')
    editer.get_comic_msg(is_gui, hang_signal, edit_line_hang) 
    editer.get_comic_chaps()
    print(editer.comic_title, editer.comic_author)
    print('*******************************')
    
    for i, chap_name in enumerate(editer.chap_name_list):
        print(f'[{str(i+1)}]', chap_name)

    print('*******************************')
    print('请输入所需要的编号进行下载（多卷可以用英文逗号分隔或直接使用连字符，详情见说明）')

def download_task(root_path,
                comic_name,
                chap_no_list,
                url,
                high_quality,
                num_thread,
                is_gui=False,
                hang_signal=None,
                progressring_signal=None,
                cover_signal=None,
                edit_line_hang=None):
    
    downloader = Downloader(comic_name=comic_name, root_path=root_path, url=url, high_quality=high_quality, num_thread=num_thread)
    print('正在积极地获取漫画信息....')
    downloader.get_comic_msg(is_gui, hang_signal, edit_line_hang) 
    downloader.get_comic_chaps()
    print(downloader.comic_title, downloader.comic_author)
    
    print('****************************')
    print('正在下载漫画....')
    for chap_no in chap_no_list:
        chap_name = downloader.chap_name_list[chap_no-1]
        chap_uuid = downloader.chap_uuid_list[chap_no-1]
        page_num = downloader.chap_pagenum_list[chap_no-1]
        downloader.download_single_chap(chap_name, chap_uuid, page_num, is_gui=is_gui, signal=progressring_signal)
        downloader.get_cover(chap_name=chap_name, is_gui=is_gui, signal=cover_signal)
    downloader.download_cover()
    print('漫画下载成功！', f'漫画路径【{downloader.comic_path}】')
    chap_list = [downloader.chap_name_list[chap_no-1] for chap_no in chap_no_list]
    editer = Editer(downloader.comic_title, downloader.comic_author, downloader.brief, downloader.tag_list,chap_list, downloader.comic_path, root_path, delete_comic=0)
    editer.pack_img()
    editer.typesetting()
    editer.get_epub()
    
    

def downloader_router(root_path,
                      comic_name,
                      chap_no,
                      url,
                      high_quality, 
                      is_gui=False, 
                      num_thread=4,
                      hang_signal=None,
                      progressring_signal=None,
                      cover_signal=None,
                      edit_line_hang=None):
    if len(comic_name)==0:
        print('请检查输入是否完整正确！')
        return
    elif chap_no == '':
        query_chaps(comic_name, url, is_gui, hang_signal, edit_line_hang)
        return 
    elif chap_no.isdigit():
        chap_no = int(chap_no)
        chap_no_list = [chap_no]
        if chap_no<=0:
            print('请检查输入是否完整正确！') 
            return
    elif "-" in chap_no:
        start, end = map(str, chap_no.split("-"))
        if start.isdigit() and end.isdigit() and int(start)>0 and int(start)<int(end):
            chap_no_list = list(range(int(start), int(end) + 1))
        else:
            print('请检查输入是否完整正确！')
            return
    elif "," in chap_no:
        chap_no_list = [num for num in chap_no.split(",")]
        if all([num.isdigit() for num in chap_no_list]):
            chap_no_list = [int(num) for num in chap_no_list] 
        else:
            print('请检查输入是否完整正确！')
            return
    else:
            print('请检查输入是否完整正确！')
            return
    download_task(root_path, comic_name, chap_no_list, url, high_quality, num_thread, is_gui, hang_signal, progressring_signal, cover_signal, edit_line_hang)
    print('所有下载任务都已经完成！')