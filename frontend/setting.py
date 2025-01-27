from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QWidget
from qfluentwidgets import (Theme, PushSettingCard, SettingCardGroup, ExpandLayout, Theme, Theme, OptionsSettingCard, OptionsConfigItem, OptionsValidator, RangeSettingCard, SwitchSettingCard, ScrollArea, RangeValidator, RangeConfigItem, BoolValidator)

from qfluentwidgets import FluentIcon as FIF
from .cfg_utils import read_config_dict, write_config_dict
from .gui_utils import Url
import os
import shutil

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