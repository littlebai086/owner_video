# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 10:57:23 2024

@author: peter
"""

import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, 
    QVBoxLayout, QWidget, QSlider, QHBoxLayout
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QUrl, Slot
import subprocess

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频播放器")

        # 初始化播放器

        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        # self.media_player.setAudioOutput(None)
        self.media_player.setAudioOutput(self.audio_output)
        # 禁用硬件加速（可选，根据需求）
        self.media_player.setProperty("threads", 1)
        self.media_player.setProperty("playbackMode", "software")
        self.media_player.setProperty("enableHardwareAcceleration", False)

        # 视频窗口
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        # 文件选择按钮
        self.open_button = QPushButton("选择视频文件")
        self.open_button.clicked.connect(self.open_file)

        # 播放/暂停按钮
        self.play_button = QPushButton("播放")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.toggle_play)

        # 进度条
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.sliderMoved.connect(self.set_position)

        # 布局
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.play_button)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.slider)
        layout.addLayout(control_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 信号绑定
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.playbackStateChanged.connect(self.update_play_button)

    @Slot()
    def open_file(self):
        """打开文件选择对话框"""
        file_dialog = QFileDialog(self)
        file_dialog.setMimeTypeFilters(["video/mp4", "video/x-matroska"])
        if file_dialog.exec() == QFileDialog.Accepted:
            url = file_dialog.selectedUrls()[0]
            print(url)
            self.media_player.setSource(url)
            self.videoWidget = QVideoWidget()
            self.player.setVideoOutput(self.videoWidget)
            self.videoWidget.show()
            # input_path = url.toLocalFile()
            # converted_path = self.transcode_video(input_path)
            # self.media_player.setSource(QUrl.fromLocalFile(converted_path))
            self.play_button.setEnabled(True)
            self.slider.setEnabled(True)
            self.media_player.play()

    @Slot()
    def toggle_play(self):
        """播放或暂停"""
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    @Slot()
    def update_position(self, position):
        """更新进度条位置"""
        self.slider.setValue(position)

    @Slot()
    def update_duration(self, duration):
        """设置进度条最大值"""
        self.slider.setRange(0, duration)

    @Slot()
    def set_position(self, position):
        """设置播放位置"""
        print(position)
        self.media_player.pause()
        self.media_player.setPosition(position)
        self.media_player.play()


    @Slot()
    def update_play_button(self, state):
        """更新播放按钮文字"""
        if state == QMediaPlayer.PlayingState:
            self.play_button.setText("暂停")
        else:
            self.play_button.setText("播放")

    def transcode_video(self, input_path):
        """使用 FFmpeg 转码为兼容格式"""
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_converted.mp4"

        # FFmpeg 转码命令
        command = [
            "ffmpeg",
            "-nostdin",  # 禁用交互
            "-i", input_path,          # 输入文件
            "-c:v", "libx264",         # 视频编码格式
            # "-preset", "fast",         # 编码速度
            "-crf", "23",              # 视频质量
            "-c:a", "aac",             # 音频编码格式
            "-b:a", "192k",            # 音频比特率
            "-y",                      # 自动覆盖输出文件
            output_path                # 输出文件
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Transcoding complete: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Error during transcoding: {e}")
            return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.resize(800, 600)
    player.show()
    sys.exit(app.exec())
