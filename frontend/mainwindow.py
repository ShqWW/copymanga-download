# coding:utf-8
from PyQt5.QtCore import QTimer, QSize, pyqtSignal 
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import (setTheme, Theme, Theme, setTheme, Theme, FluentWindow, NavigationItemPosition, qconfig, SplashScreen)

from qfluentwidgets import FluentIcon as FIF
import base64
from resource.logo import logo_base64
from resource.logo_big import logo_big_base64
from backend.copymanga.router import *

from frontend.cfg_utils import *
from frontend.gui_utils import font_label
from frontend.copymanga_gui import HomeWidget
from frontend.setting import SettingWidget



class MainWindow(FluentWindow):
    update_signal = pyqtSignal(object) 
    def __init__(self):
        super().__init__()

        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(logo_big_base64))
        self.splashScreen = SplashScreen(QIcon(pixmap), self)
        self.splashScreen.setIconSize(QSize(250, 250))
        self.splashScreen.raise_()
        initialize_db()

        self.head = 'https://www.copymanga.tv'
        split_str = '**************************************\n    '
        self.welcome_text = f'使用说明：\n{split_str}1.拷贝漫画{self.head}，根据漫画网址输入漫画名以及下载话对应的号码。例如漫画网址是{self.head}/comic/yaoyeluying，则漫画名输入yaoyeluying。\n{split_str}2.要查询漫画编号等信息，则可以只输入漫画名不输入编号，点击确定会返回话名称和对应的编号。\n{split_str}3.输入下载的编号，要下载编号[2]对应话，则编号输入2。想下载多话比如[1]至[3]对应话，则编号输入1-3或1,2,3（英文逗号分隔，编号可以不连续）。'
        self.homeInterface = HomeWidget('Home Interface', self)
        self.settingInterface = SettingWidget('Setting Interface', self)
        self.initNavigation()
        self.initWindow()

        QTimer.singleShot(50, lambda: self.set_theme(read_config_dict('theme')))
        QTimer.singleShot(2000, lambda: self.splashScreen.close())
        
    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主界面')
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(700, 460)
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(logo_base64))
        self.setWindowIcon(QIcon(pixmap))
        self.setWindowTitle('拷贝漫画下载器')
        self.setFont(font_label)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
    
    def set_theme(self, mode=None):
        if mode=='Light':
            setTheme(Theme.LIGHT)
        elif mode=='Dark':
            setTheme(Theme.DARK)
        elif mode== 'Auto':
            setTheme(Theme.AUTO)
        theme = qconfig.theme
        if theme == Theme.DARK:
            self.homeInterface.label_book.setTextColor(QColor(255,255,255))
            self.homeInterface.label_volumn.setTextColor(QColor(255,255,255))
        elif theme == Theme.LIGHT:
            self.homeInterface.label_book.setTextColor(QColor(0,0,0))
            self.homeInterface.label_volumn.setTextColor(QColor(0,0,0))
