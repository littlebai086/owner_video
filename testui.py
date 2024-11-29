# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 10:48:26 2024

@author: peter
"""
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QHBoxLayout

class DeviceSelectionPage(QWidget):
    def __init__(self, switch_to_main_ui):
        super().__init__()
        self.setWindowTitle("设备选择")
        
        # 设备列表
        self.list_devices = ["GPU:0 (NVIDIA GeForce RTX 3060)", "GPU:1 (NVIDIA GeForce RTX 3090)", "CPU"]
        
        # 创建ComboBox
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(self.list_devices)

        # 创建按钮来获取选择的值并进入下一页
        self.select_button = QPushButton("选择设备并进入主界面", self)
        self.select_button.clicked.connect(self.on_select_device)

        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.select_button)
        
        self.setLayout(layout)
        self.switch_to_main_ui = switch_to_main_ui

    def on_select_device(self):
        """获取选择的设备并进入主界面"""
        selected_device = self.combo_box.currentText()  # 获取当前选择的项
        print(f"选择的设备: {selected_device}")
        
        # 切换到主界面
        self.switch_to_main_ui(selected_device)


class MainUIPage(QWidget):
    def __init__(self, selected_device, switch_to_device_selection):
        super().__init__()
        self.setWindowTitle("主界面")
        
        # 显示设备信息
        self.device_label = QLabel(f"当前选择的设备: {selected_device}", self)

        # 其他主界面控件
        self.main_content_label = QLabel("这里是主界面的其他内容", self)

        # 返回按钮
        self.back_button = QPushButton("返回设备选择", self)
        self.back_button.clicked.connect(self.on_back_button_clicked)

        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.device_label)
        layout.addWidget(self.main_content_label)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

        self.switch_to_device_selection = switch_to_device_selection

    def on_back_button_clicked(self):
        """点击返回按钮时切换回设备选择界面"""
        self.switch_to_device_selection()


class VideoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("设备选择与主界面")
        
        # 创建 QStackedWidget 来管理页面切换
        self.stacked_widget = QStackedWidget(self)

        # 创建页面
        self.device_selection_page = DeviceSelectionPage(self.switch_to_main_ui)
        self.main_ui_page = None  # 初始化主界面为空

        # 将页面添加到 QStackedWidget
        self.stacked_widget.addWidget(self.device_selection_page)
        
        # 设置布局
        layout = QHBoxLayout(self)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def switch_to_main_ui(self, selected_device):
        """切换到主界面"""
        # 创建主界面并切换
        self.main_ui_page = MainUIPage(selected_device, self.switch_to_device_selection)
        self.stacked_widget.addWidget(self.main_ui_page)
        self.stacked_widget.setCurrentWidget(self.main_ui_page)  # 显示主界面

    def switch_to_device_selection(self):
        """切换回设备选择页面"""
        self.stacked_widget.setCurrentWidget(self.device_selection_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec())
