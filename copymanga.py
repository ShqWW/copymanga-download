import argparse
from backend.copymanga.router import downloader_router
import os

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='config')
    parser.add_argument('--comic_no', default='0000', type=str)
    parser.add_argument('--volume_no', default='1', type=int)
    parser.add_argument('--no_input', default=False, type=bool)
    args = parser.parse_args()
    return args
    
if __name__=='__main__':
    args = parse_args()
    download_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    if args.no_input:
        downloader_router(root_path='out', comic_name=args.comic_no, chap_no=args.volume_no)
    else:
        while True:
            args.comic_name = input('请输入漫画名称：')
            args.volume_no = input('请输入话数(查看目录信息不输入直接按回车，下载多卷请使用逗号分隔或者连字符-)：')
            # args.comic_name = 'xinglingganying'
            # args.volume_no = '1-3'
            downloader_router(root_path='out', comic_name=args.comic_name, chap_no=args.volume_no, url='mangacopy.com', high_quality=True, num_thread=4)
            # exit(0)
    
        

    

    
    
