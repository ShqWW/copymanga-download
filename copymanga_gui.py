# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QFileDialog, QWidget
from qfluentwidgets import (setTheme, Theme, PushSettingCard, SettingCardGroup, ExpandLayout, TextEdit, ImageLabel, LineEdit, PushButton, ProgressRing, OptionsSettingCard, OptionsConfigItem, OptionsValidator, FluentWindow, SubtitleLabel, NavigationItemPosition, setThemeColor, qconfig, ComboBox, SwitchSettingCard, RangeSettingCard, BoolValidator, ScrollArea, RangeConfigItem, RangeValidator, SplashScreen)
from qfluentwidgets import FluentIcon as FIF
import sys
import base64
import shutil
from resource.logo import logo_base64
from resource.logo_big import logo_big_base64
from resource.book import book_base64
from copymanga import *
from enum import Enum
from cfg_utils import *

font_label = QFont('微软雅黑', 18)
font_msg = QFont('微软雅黑', 10)

class MainThread(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
    def run(self):
        self.parent.clear_signal.emit('')
        try:
            comic_no = self.parent.editline_book.text()
            chap_no = self.parent.editline_volumn.text()
            url = read_config_dict("url")
            high_quality = bool(int(read_config_dict("quality")))
            thread_num = int(read_config_dict("numthread"))
            download_path = read_config_dict("download_path")
            downloader_router(download_path, comic_no, chap_no, url, high_quality, True, thread_num, self.parent.hang_signal, self.parent.progressring_signal, self.parent.cover_signal, self.parent.editline_hang)
            self.parent.end_signal.emit('')
        except Exception as e:
            self.parent.end_signal.emit('')
            print('错误，请检查网络情况或确认输入是否正确')
            print('错误信息：')
            print(e)
    def terminate(self) -> None:
        result = super().terminate()
        return result

class EmittingStr(QObject):
    textWritten = pyqtSignal(str)  # 定义一个发送str的信号
    def write(self, text):
        self.textWritten.emit(str(text))
    def flush(self):
        pass
    def isatty(self):
        pass


class Url(Enum):
    """ Theme enumeration """

    TV = "copymanga.tv"
    COM = "mangacopy.com"

class SettingWidget(ScrollArea):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.parent = parent
        self.setting_group = SettingCardGroup(self.tr("设置"), self.scrollWidget)

        
        self.download_path_card = PushSettingCard(
            self.tr('选择文件夹'),
            FIF.DOWNLOAD,
            self.tr("下载目录"),
            read_config_dict("download_path"),
            self.setting_group
        )

        theme_name = read_config_dict('theme')
        if theme_name == 'Light':
            self.themeMode = OptionsConfigItem(None, "ThemeMode", Theme.LIGHT, OptionsValidator(Theme), None)
        elif theme_name == 'Dark':
            self.themeMode = OptionsConfigItem(None, "ThemeMode", Theme.DARK, OptionsValidator(Theme), None)
        else:
            self.themeMode = OptionsConfigItem(None, "ThemeMode", Theme.AUTO, OptionsValidator(Theme), None)

        self.theme_card = OptionsSettingCard(
            self.themeMode,
            FIF.BRUSH,
            self.tr('应用主题'),
            self.tr("更改外观"),
            texts=[
                self.tr('亮'), self.tr('暗'),
                self.tr('跟随系统')
            ],
            parent=self.parent
        )

        if read_config_dict("url").endswith('tv'):
            url_option = OptionsConfigItem(None, "urlMode", Url.TV, OptionsValidator(Url), None)
        else: 
            url_option = OptionsConfigItem(None, "urlMode", Url.COM, OptionsValidator(Url), None)
        
        self.url_card = OptionsSettingCard(
            url_option,
            FIF.VPN,
            self.tr('漫画域名切换'),
            self.tr("切换域名"),
            texts=[
                self.tr("copymanga.tv"), self.tr("mangacopy.com"),
            ],
            parent=self.parent
        )

        self.thread_card = RangeSettingCard(
            RangeConfigItem("thread", "下载线程数量", int(read_config_dict("numthread")), RangeValidator(1, 16)),
            FIF.SPEED_HIGH,
            self.tr('图片下载线程数量'),
            self.tr('适当增加充分利用带宽,但不要太高'),
            self.setting_group
        ) 

        is_high_quality = (read_config_dict("quality") == '1')
        if is_high_quality:
            self.qualityMode = OptionsConfigItem(None, "QualityMode", True, BoolValidator())
        else:
            self.qualityMode = OptionsConfigItem(None, "QualityMode", False, BoolValidator())
        self.quality_card = SwitchSettingCard(
            FIF.LEAF,
            self.tr('下载高质量图片'),
            self.tr('开启后会提高漫画清晰度，但会增加下载漫画的体积'),
            parent=self.parent,
            configItem=self.qualityMode
        )
        self.quality_card.switchButton.setText(
            self.tr('高') if is_high_quality else self.tr('低'))


        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 10, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface2')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        qss = '''
                SettingInterface, #scrollWidget {
                    background-color: transparent;
                }

                QScrollArea {
                    border: none;
                    background-color: transparent;
                }

                QLabel#settingLabel {
                    font: 33px 'Microsoft YaHei Light';
                    background-color: transparent;
                    color: white;
                }

                '''
        
        self.setStyleSheet(qss)

        self.setting_group.addSettingCard(self.download_path_card)
        self.setting_group.addSettingCard(self.thread_card)
        self.setting_group.addSettingCard(self.quality_card)
        self.setting_group.addSettingCard(self.url_card)
        self.setting_group.addSettingCard(self.theme_card)
        
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(20, 10, 20, 0)
        self.expandLayout.addWidget(self.setting_group)

        self.download_path_card.clicked.connect(self.download_path_changed)
        self.theme_card.optionChanged.connect(self.theme_changed)
        self.url_card.optionChanged.connect(self.url_changed)
        self.thread_card.valueChanged.connect(self.thread_changed)
        self.quality_card.checkedChanged.connect(self.quality_changed)

    def download_path_changed(self):
        """ download folder card clicked slot """
        out_path = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), read_config_dict("download_path"))
        write_config_dict("download_path", out_path)
        self.download_path_card.contentLabel.setText(read_config_dict("download_path"))
    
    def theme_changed(self):
        theme_name = self.theme_card.choiceLabel.text()
        if theme_name == '亮':
            theme_mode = 'Light' 
        elif theme_name == '暗':
            theme_mode = 'Dark' 
        elif theme_name == '跟随系统':
            theme_mode = 'Auto' 
        write_config_dict("theme", theme_mode)
        self.parent.set_theme(read_config_dict("theme"))
        if os.path.exists('./config'):
            shutil.rmtree('./config')

    def url_changed(self):
        write_config_dict("url", self.url_card.choiceLabel.text())
        if os.path.exists('./config'):
            shutil.rmtree('./config')

    def thread_changed(self):
        num_thread = self.thread_card.valueLabel.text()
        write_config_dict("numthread", num_thread)
        if os.path.exists('./config'):
            shutil.rmtree('./config')

    def quality_changed(self):
        is_checked = self.quality_card.isChecked()
        if is_checked:
            write_config_dict("quality", "1")
        else:
            write_config_dict("quality", "0")

        self.quality_card.switchButton.setText(
            self.tr('高') if  read_config_dict("quality")=='1' else self.tr('低'))
        if os.path.exists('./config'):
            shutil.rmtree('./config')
        

            

class HomeWidget(QFrame):

    progressring_signal = pyqtSignal(object) 
    end_signal = pyqtSignal(object) 
    hang_signal = pyqtSignal(object)
    clear_signal = pyqtSignal(object)
    cover_signal = pyqtSignal(object)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text)
        self.parent = parent
        self.label_book = SubtitleLabel('名称：', self)
        self.label_volumn = SubtitleLabel('编号：', self)
        self.editline_book = LineEdit(self) 
        self.editline_volumn = LineEdit(self) 
        
        
        # self.editline_book.setText('yaoyeluying')
        # self.editline_volumn.setText('3')
        
        self.book_icon = QPixmap()
        self.book_icon.loadFromData(base64.b64decode(book_base64))
        self.cover_w, self.cover_h = 152, 230

        self.label_cover = ImageLabel(self.book_icon, self)
        self.label_cover.setBorderRadius(8, 8, 8, 8)
        self.label_cover.setFixedSize(self.cover_w, self.cover_h)

        self.text_screen = TextEdit()
        self.text_screen.setReadOnly(True)
        self.text_screen.setFixedHeight(self.cover_h)

        self.progressRing = ProgressRing(self)
        self.progressRing.setValue(0)
        self.progressRing.setTextVisible(True)
        self.progressRing.setFixedSize(50, 50)
        
        self.btn_run = PushButton('确定', self)
        self.btn_run.setShortcut(Qt.Key_Return)
        self.btn_stop = PushButton('取消', self)
        self.btn_hang = PushButton('确定', self)
        
        self.editline_hang = ComboBox(self)
        self.gridLayout = QGridLayout(self)
        self.screen_layout = QGridLayout()
        self.btn_layout = QGridLayout()
        self.hang_layout = QGridLayout()
        
        self.label_book.setFont(font_label)
        self.label_volumn.setFont(font_label)
        self.editline_book.setFont(font_label)
        self.editline_volumn.setFont(font_label)
        self.text_screen.setFont(font_msg)
        self.editline_hang.setFont(font_msg)

        self.gridLayout.addWidget(self.editline_book, 0, 1)
        self.gridLayout.addWidget(self.editline_volumn, 1, 1)
        self.gridLayout.addWidget(self.label_book, 0, 0)
        self.gridLayout.addWidget(self.label_volumn, 1, 0)

        self.gridLayout.addLayout(self.btn_layout, 2, 1, 1, 1)
        self.btn_layout.addWidget(self.btn_run, 2, 1)
        self.btn_layout.addWidget(self.btn_stop, 2, 2)

        self.gridLayout.addLayout(self.screen_layout, 3, 0, 2, 2)

        self.screen_layout.addWidget(self.progressRing, 0, 0, Qt.AlignRight|Qt.AlignBottom)
        self.screen_layout.addWidget(self.text_screen, 0, 0)
        self.screen_layout.addWidget(self.label_cover, 0, 1)
        
        

        self.gridLayout.addLayout(self.hang_layout, 5, 0, 1, 2)
        self.hang_layout.addWidget(self.editline_hang, 0, 0)
        self.hang_layout.addWidget(self.btn_hang, 0, 1)

        self.screen_layout.setContentsMargins(0,0,0,0)
        self.btn_layout.setContentsMargins(0,0,0,0)
        self.gridLayout.setContentsMargins(20, 10, 20, 10)

        self.btn_run.clicked.connect(self.process_start)
        self.btn_stop.clicked.connect(self.process_stop)
        self.btn_hang.clicked.connect(self.process_continue)

        self.progressring_signal.connect(self.progressring_msg)
        self.end_signal.connect(self.process_end)
        self.hang_signal.connect(self.process_hang)
        self.clear_signal.connect(self.clear_screen)
        self.cover_signal.connect(self.display_cover)

        self.progressRing.hide()
        self.btn_hang.hide()
        self.editline_hang.hide()
        self.btn_stop.setEnabled(False)
        
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)
        self.text_screen.setText(self.parent.welcome_text) 
    
    def process_start(self):
        self.label_cover.setImage(self.book_icon)
        self.label_cover.setFixedSize(self.cover_w, self.cover_h)
        self.btn_run.setEnabled(False)
        self.btn_run.setText('正在下载')
        self.btn_stop.setEnabled(True)
        self.main_thread = MainThread(self)
        self.main_thread.start()
        
    def process_end(self, input=None):
        self.btn_run.setEnabled(True)
        self.btn_run.setText('开始下载')
        self.btn_run.setShortcut(Qt.Key_Return)
        self.btn_stop.setEnabled(False)
        self.progressRing.hide()
        self.btn_hang.hide()
        self.editline_hang.clear()
        self.editline_hang.hide()
        if input=='refresh':
            self.label_cover.setImage(self.book_icon)
            self.label_cover.setFixedSize(self.cover_w, self.cover_h)
            self.clear_signal.emit('')
            self.text_screen.setText(self.parent.welcome_text) 
        
    def outputWritten(self, text):
        cursor = self.text_screen.textCursor()
        scrollbar=self.text_screen.verticalScrollBar()
        is_bottom = (scrollbar.value()>=scrollbar.maximum() - 15)
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        if is_bottom:
            self.text_screen.setTextCursor(cursor)
        # self.text_screen.ensureCursorVisible()
    
    def clear_screen(self):
        self.text_screen.clear()
    
    def display_cover(self, signal_msg):
        filepath, img_h, img_w = signal_msg
        self.label_cover.setImage(filepath)
        self.label_cover.setFixedSize(int(img_w*self.cover_h/img_h), self.cover_h)
        
    def progressring_msg(self, input):
        if input == 'start':
            self.progressRing.setValue(0)
            self.progressRing.show()
        elif input == 'end':
            self.progressRing.hide()
            self.progressRing.setValue(0)
        else:
            self.progressRing.setValue(input)
    
    def process_hang(self, input=None):
        self.btn_hang.setEnabled(True)
        self.btn_hang.setShortcut(Qt.Key_Return)
        self.btn_hang.show()
        self.editline_hang.show()
    
    def process_continue(self, input=None):
        self.btn_hang.hide()
        self.btn_hang.setEnabled(False)
        self.editline_hang.hide()
        
    
    def process_stop(self):
        self.main_thread.terminate()
        self.end_signal.emit('refresh')
        
        
    

class Window(FluentWindow):
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


    
if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    setTheme(Theme.DARK)
    setThemeColor('#1E90FF')
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
