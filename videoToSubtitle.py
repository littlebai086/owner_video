# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 15:58:58 2024

@author: peter
"""
import sys
# from PyQt6.QtWidgets import (
#     QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
#     QSlider, QProgressBar, QFileDialog
# )
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget, QLabel, QHBoxLayout, QSlider, QTextEdit, QFileDialog

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from moviepy.editor import VideoFileClip
import os
import shutil
from googletrans import Translator
import whisper

class VideoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.speech_recognition_text=""
        self.translate_text=""
        self.all_speech_recognition_text=""
        self.initUI()
        self.model = whisper.load_model("small")

    def initUI(self):
        self.setWindowTitle("视频语音转文字工具")
        self.setGeometry(100, 100, 600, 300)

        # 主布局
        layout = QVBoxLayout()

        # 文件选择部分
        file_layout = QHBoxLayout()
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("color: gray; font-size: 14px;")
        self.select_file_button = QPushButton("选择影片")
        self.select_file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_file_button)
        layout.addLayout(file_layout)

        # 进度条部分
        progress_layout = QHBoxLayout()
        self.progress_bar = QSlider(Qt.Orientation.Horizontal)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.sliderReleased.connect(self.seek_video)
        self.progress_label = QLabel("0%")
        progress_layout.addWidget(QLabel("播放进度："))
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)

        # 控制按钮部分
        control_layout = QHBoxLayout()
        self.play_button = QPushButton("播放")
        self.play_button.clicked.connect(self.play_pause)
        self.speech_to_text_button = QPushButton("語音轉文字")
        self.speech_to_text_button.clicked.connect(self.start_speech_to_text)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.speech_to_text_button)
        layout.addLayout(control_layout)

        # 状态信息部分
        self.status_label = QLabel("状态：准备中")
        self.status_label.setStyleSheet("color: blue; font-size: 14px;")
        layout.addWidget(self.status_label)
        
        # 語音辨識後的Label
        self.speech_recognition_label = QLabel("語音辨識的文字")
        self.speech_recognition_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.speech_recognition_label)
        
        # 語音辨識後的Text
        self.speech_recognition_textEdit = QTextEdit()
        self.speech_recognition_textEdit.setReadOnly(True)  # 设置为只读
        layout.addWidget(self.speech_recognition_textEdit)
                
        # 翻譯後的文字的Label
        self.translate_label = QLabel("翻譯後的文字")
        self.translate_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.translate_label)
        
        # 翻譯後的文字的Text
        self.translate_textEdit = QTextEdit()
        self.translate_textEdit.setReadOnly(True)  # 设置为只读
        layout.addWidget(self.translate_textEdit)
       
        # 原本的語音內容及秒數的Label
        self.all_speech_recognition_label = QLabel("原本的語音內容及秒數")
        self.all_speech_recognition_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.all_speech_recognition_label)
        
        # 原本的語音內容及秒數的Text
        self.all_speech_recognition_textEdit = QTextEdit()
        self.all_speech_recognition_textEdit.setReadOnly(True)  # 设置为只读
        layout.addWidget(self.all_speech_recognition_textEdit)
        
        # 设置主布局
        self.setLayout(layout)

        # 初始化其他属性
        self.video_file = None
        self.playing = False

    def select_file(self):
        """选择视频文件"""
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mkv *.mov)"
        )
        if file_path:
            self.video_file = file_path
            self.file_label.setText(f"已选择文件：{file_path.split('/')[-1]}")
            self.progress_bar.setValue(0)
            self.status_label.setText("状态：文件已加载")
        else:
            self.status_label.setText("状态：未选择文件")

    def play_pause(self):
        """播放或暂停视频"""
        if not self.video_file:
            self.status_label.setText("状态：请先选择文件")
            return

        if self.playing:
            self.play_button.setText("播放")
            self.status_label.setText("状态：已暂停")
            self.playing = False
        else:
            self.play_button.setText("暂停")
            self.status_label.setText("状态：播放中")
            self.playing = True

    def seek_video(self):
        """调整播放进度"""
        value = self.progress_bar.value()
        self.progress_label.setText(f"{value}%")
        self.status_label.setText(f"状态：调整到 {value}%")

    def start_speech_to_text(self):
        """启动语音转文字"""
        if not self.video_file:
            self.status_label.setText("状态：请先选择文件")
            return
        print(self.video_file)
        self.status_label.setText("状态：正在进行语音转文字...")
        output_audio = self.extract_audio(self.video_file)
        [speech_recognition_text,all_speech_recognition_text] = self.transcribe_audio(output_audio)
        translate_text = self.translate_text(speech_recognition_text)
        
        # 模拟语音转文字处理
        self.speech_to_text_processing()

    def text_edit_to_show(self,speech_recognition_text,translate_text,all_speech_recognition_text):
        self.speech_recognition_text.clear()  # 清除之前的内容
        self.translate_text.clear()  # 清除之前的内容
        # self.speech_recognition_textEdit.append("语音识别结果：")
        self.speech_recognition_textEdit.append(speech_recognition_text)
        
        self.translate_textEdit.clear()
        self.translate_textEdit.append(translate_text)
        
        self.all_speech_recognition_textEdit.clear()
        self.all_speech_recognition_textEdit.append(all_speech_recognition_text)
        
        # 更新状态标签
        self.status_label.setText("状态：语音转文字完成")
        
    def speech_to_text_processing(self):
        """模拟语音转文字的后台处理"""
        # 假设我们用一个库（如whisper）将视频中的语音转换为文字
        recognized_text = "这是识别的文字。"

        # 假设我们将识别的文字翻译成英语
        translated_text = "This is the recognized text."

        
        # 将识别和翻译的文本更新到 QTextEdit 中
        self.speech_recognition_text.clear()  # 清除之前的内容
        self.translate_text.clear()  # 清除之前的内容
        self.speech_recognition_text.append("语音识别结果：")
        self.speech_recognition_text.append(recognized_text)
        self.speech_recognition_text.append("")  # 空行分隔
        self.speech_recognition_text.append("翻译结果：")
        self.translate_text.append(translated_text)

        # 更新状态标签
        self.status_label.setText("状态：语音转文字完成")

    def transcribe_audio(self, audio_path):
        """將音訊轉為文字"""
        print("將音訊轉為文字")
        # recognizer = sr.Recognizer()
        try:
            result = self.model.transcribe(audio_path)  # 支持 MP3, WAV, FLAC 格式
            text = ""
            all_text = ""
            for segment in result["segments"]:
                text += f"{segment['text']}\r\n"
                all_text += f"Start: {segment['start']}s, End: {segment['end']}s, Text: {segment['text']}\r\n"
                print(f"Start: {segment['start']}s, End: {segment['end']}s, Text: {segment['text']}")
            print("開始轉錄...")
            print(audio_path)
            return [text,all_text]
        except Exception as e:
            print(f"讀取音訊時出錯: {e}")
            return [None,None]
        
    def translate_text(self,text):
        """翻譯文字為繁體中文"""
        print("翻譯文字為繁體中文")
        translator = Translator()
        return translator.translate(text, src='en', dest='zh-TW').text

    def extract_audio(self, video_file):
        """从视频文件中提取音频并保存为 WAV 格式"""
        
        # 获取当前执行的文件目录
        current_dir = os.getcwd()
        print(current_dir)
        # 提取文件名（不包括路径和扩展名）
        file_name_without_extension = os.path.splitext(os.path.basename(video_file))[0]
        
        # 构造输出音频文件路径，放在当前目录下
        output_audio = os.path.join(current_dir, file_name_without_extension + ".wav")
        
        
        # 复制视频文件到当前目录
        output_video = os.path.join(current_dir, os.path.basename(video_file))

        try:
            shutil.copy(video_file, output_video)
            # 读取视频文件
            video = VideoFileClip(video_file)
            
            # 提取音频
            audio = video.audio
            
            # 保存音频为 WAV 格式
            audio.write_audiofile(output_audio, codec='pcm_s16le')
            print(f"音频已保存为：{output_audio}")
            return output_audio
        except Exception as e:
            print(f"提取音频时发生错误: {e}")
            return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec())
