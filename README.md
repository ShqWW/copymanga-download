
<div align="center">
  <img src="resource/logo.png" width="150" style="margin-right: 3000px;"/> 
</div>

<h1 align="center">
  &nbsp;&nbsp;&nbsp;&nbsp;拷贝漫画EPUB下载器
</h1>





[拷贝漫画](https://www.copymanga.site)(copymanga)下载, 并打包为EPUB格式。

特性:

* Fluent Design风格界面，下载进度与漫画封面显示，主题切换，下载目录自定义。
* 前后端分离，同时支持命令行版本。
* 章节批量下载。
* EPUB格式自动打包。
* 图片质量自定义选择。
* 断点续传，避免重复下载。
* 多线程预缓存策略，下载速度快。
* 网站域名自定义更换，防止被墙。
* ...................


有建议或bug可以提issue，也可以加QQ群获得更多信息：563072544

图形界面使用[PyQt-Fluent-Widgets](https://pyqt-fluent-widgets.readthedocs.io/en/latest/index.html)界面编写。

[release](https://github.com/ShqWW/copymanga-download/releases)页面发布了已经打包好的exe可执行程序，包括图形化版本和命令行版本(系统最低要求Windows 10)。

界面样例：
<div align="center">
  <img src="resource/example1.png" width="400"/>
  <img src="resource/example2.png" width="400"/>
</div>

## 使用前安装需要的包
```
pip install -r requirements.txt -i https://pypi.org/simple/
```
## 使用命令行模式运行(无需安装图形界面库，支持Linux):
```
python copymanga.py
```

## 使用图形界面运行:
```
python copymanga_gui.py
```

## 使用pyinstaller打包:
```
pip install pyinstaller
```
```
pyinstaller -F -w -i .\resource\logo.png .\copymanga_gui.py 
```

## 相关项目：

* [轻小说文库EPUB下载器](https://github.com/ShqWW/lightnovel-download)

* [哔哩轻小说EPUB下载器](https://github.com/ShqWW/bilinovel-download)

* [拷贝漫画EPUB下载器](https://github.com/ShqWW/copymanga-download)

## EPUB漫画漫画编辑和管理工具推荐：
1. [Sigil](https://sigil-ebook.com/) 
2. [Calibre](https://www.calibre-ebook.com/)

