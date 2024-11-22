# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 16:48:13 2024

@author: peter
"""
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl
import sys

class VideoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle("PyQt6 QMediaPlayer 示例")
        self.resize(800, 600)

        # 创建布局
        layout = QVBoxLayout()

        # 视频显示小部件
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)

        # 播放按钮
        self.play_button = QPushButton("播放")
        self.play_button.clicked.connect(self.play_video)
        layout.addWidget(self.play_button)

        # 创建 QMediaPlayer 和音频输出
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        self.setLayout(layout)

    def play_video(self):
        # 设置视频源
        video_url = QUrl.fromLocalFile("See_You_Again_Part.mp4")  # 替换为你的视频路径
        self.media_player.setSource(video_url)

        # 播放视频
        self.media_player.play()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec())
