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
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget, QLabel, QHBoxLayout, QSlider, QTextEdit, QFileDialog, QMessageBox,QProgressBar 

from PyQt6.QtCore import Qt, QThread, pyqtSignal,QTimer
from PyQt6.QtGui import QIcon
from moviepy.editor import VideoFileClip
import os
import shutil
from googletrans import Translator
from datetime import datetime
import time
from pydub.utils import mediainfo
import whisper

class VideoProcessThread(QThread):
    progress_signal = pyqtSignal(int)
    error_signal = pyqtSignal(str)
    transcribed_signal = pyqtSignal(str)
    translated_signal = pyqtSignal(str)
    all_transcribed_signal = pyqtSignal(str)
    subtitles_signal = pyqtSignal(list)

    def __init__(self, video_path, audio_path):
        super().__init__()
        self.video_path = video_path
        self.audio_path = audio_path
        # self.subtitles = None
        self.model = whisper.load_model("small")  # 选择 'base' 模型，适合快速测试

    def run(self):
        try:
            # 擷取音訊並轉為文字
            print("擷取音訊並轉為文字")
            audio_file = self.extract_audio(self.video_path)
            transcribed_text,all_transcribed_text,subtitles = self.transcribe_audio(audio_file)

            self.transcribed_signal.emit(transcribed_text)  # 發送轉錄文字訊號
            self.all_transcribed_signal.emit(all_transcribed_text)  # 發送轉錄文字訊號

            # 翻譯文字
            print("翻譯文字")
            translated_text = self.translate_text(transcribed_text)
            # print(translated_text)
            self.translated_signal.emit(translated_text)  # 發送翻譯文字訊號
            subtitles = self.translate_text_to_subtitles(subtitles,translated_text)
            self.subtitles_signal.emit(subtitles)
        except Exception as e:
            self.error_signal.emit(str(e))

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
            if output_video:
                if os.path.abspath(video_file) == os.path.abspath(output_video):
                    print("源文件和目标文件相同，直接覆盖")
                    os.remove(output_video)
            shutil.copy(video_file, output_video)
            # 读取视频文件
            video = VideoFileClip(video_file)
            # 保存音频为 WAV 格式
            video.audio.write_audiofile(output_audio, codec='pcm_s16le')
            print(f"音频已保存为：{output_audio}")
            return output_audio
        except Exception as e:
            print(f"提取音频时发生错误: {e}")
            return None

    def transcribe_audio(self, audio_path):
        """將音訊轉為文字"""
        print("將音訊轉為文字")
        try:
            # 設定進度回調函數
            result = self.model.transcribe(audio_path, verbose=True)  # 支持 MP3, WAV, FLAC 格式
            # 估算进度
            total_segments = len(result["segments"])
            text = ""
            all_text = ""
            for  i, segment in enumerate(result["segments"]):
                text += f"{segment['text']}\r\n"
                all_text += f"Start: {segment['start']}s, End: {segment['end']}s, Text: {segment['text']}\r\n"
                progress = int((i + 1) / total_segments * 100)
                self.progress_signal.emit(progress)  # 发送信号更新进度条
                # time.sleep(0.1)  # 模拟处理时间
                print(f"Start: {segment['start']}s, End: {segment['end']}s, Text: {segment['text']}")
            print("開始轉錄...")
            print(audio_path)
            return [text,all_text,result["segments"]]
        except Exception as e:
            print(f"讀取音訊時出錯: {e}")
            return [None,None,None]

    def translate_text(self, text):
        """翻譯文字為繁體中文"""
        if not text or not isinstance(text, str):
            # 確保輸入為非空字串
            return text
        
        translator = Translator()
        try:
            translated = translator.translate(text, src='en', dest='zh-TW')
            # 確保返回的物件有 text 屬性
            if translated and hasattr(translated, 'text'):
                return translated.text
        except Exception as e:
            print(f"翻譯失敗: {e}")
        
        # 如果翻譯失敗，返回原始文本
        return text
    
    def translate_text_to_subtitles(self,subtitles,chinese_text):
        chinese_translate_text_array = chinese_text.split("\r\n")
        for index, subtitle in enumerate(subtitles):
            subtitles[index]["chinese_text"] = chinese_translate_text_array[index]
        return subtitles
    
class VideoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.speech_recognition_text=""
        self.translate_text=""
        self.all_speech_recognition_text=""
        self.audio_path = "audio.wav"
        self.processing_seconds = 0
        # 翻譯是否完成
        self.translation_complete = False
        self.initUI()
        self.model = whisper.load_model("small")

    def initUI(self):
        self.setWindowTitle("視頻語音轉文字工具")
        self.setGeometry(100, 100, 600, 300)

        # 主布局
        layout = QVBoxLayout()

        # 文件选择部分
        file_layout = QHBoxLayout()
        self.file_label = QLabel("未選擇文件")
        self.file_label.setStyleSheet("color: gray; font-size: 14px;")
        self.select_file_button = QPushButton("選擇影片")
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
        self.speech_to_text_button.clicked.connect(self.start_speech_to_text_processing)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.speech_to_text_button)
        layout.addLayout(control_layout)

        # 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_processing_time)
        self.processing_time_label = QLabel("處理秒數：0 秒")
        self.processing_time_label.setStyleSheet("color: blue; font-size: 14px;")
        layout.addWidget(self.processing_time_label)
        
        # 状态信息部分
        self.status_label = QLabel("狀態：準備中")
        self.status_label.setStyleSheet("color: blue; font-size: 14px;")
        layout.addWidget(self.status_label)
        
        # 進度條
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        
        # 自定义进度条样式
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid grey;
                border-radius: 5px;
                background: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #00FF00;
                width: 10px;
                margin: 0.5px;
            }
        """)
        layout.addWidget(self.progress_bar)
        # 語音辨識後的Label
        self.speech_recognition_label = QLabel("語音辨識的文字")
        self.speech_recognition_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.speech_recognition_label)
        
        # 語音辨識後的Text
        self.speech_recognition_textEdit = QTextEdit()
        self.speech_recognition_textEdit.setReadOnly(True)  # 设置为只读
        layout.addWidget(self.speech_recognition_textEdit)
        
        # 語音辨識下載srt檔案的button
        self.original_srt_button = QPushButton("原文下載Srt檔案")
        self.original_srt_button.clicked.connect(self.original_srt_button_click)
        layout.addWidget(self.original_srt_button)
        
        # 翻譯後的文字的Label
        self.translate_label = QLabel("翻譯後的文字")
        self.translate_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.translate_label)
        
        # 翻譯後的文字的Text
        self.translate_textEdit = QTextEdit()
        self.translate_textEdit.setReadOnly(True)  # 设置为只读
        layout.addWidget(self.translate_textEdit)
                
        # 翻譯後的語音辨識下載srt檔案的button
        self.translate_srt_button = QPushButton("翻譯後下載Srt檔案")
        self.translate_srt_button.clicked.connect(self.translate_srt_button_click)
        layout.addWidget(self.translate_srt_button)
       
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
        self.video_file_name = None
        self.playing = False

    def select_file(self):
        """选择视频文件"""
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "選擇視頻文件", "", "視頻文件 (*.mp4 *.avi *.mkv *.mov)"
        )
        if file_path:
            normalized_path = os.path.normpath(file_path)
            self.video_file = normalized_path
            self.video_file_name = os.path.splitext(os.path.basename(normalized_path))[0]
            self.file_label.setText(f"已選擇文件：{file_path.split('/')[-1]}")
            self.progress_bar.setValue(0)
            self.status_label.setText("狀態：文件已加载")
        else:
            self.status_label.setText("狀態：未選擇文件")

    def play_pause(self):
        """播放或暂停视频"""
        if not self.video_file:
            self.status_label.setText("狀態：請先選擇文件")
            return

        if self.playing:
            self.play_button.setText("播放")
            self.status_label.setText("狀態：已暂停")
            self.playing = False
        else:
            self.play_button.setText("暂停")
            self.status_label.setText("狀態：播放中")
            self.playing = True

    def original_srt_button_click(self):
        """翻譯後的srt button 點擊"""
        if not self.translation_complete:
            QMessageBox.critical(self, "錯誤", "尚未上傳文件或開始語音轉文字")
            return
        default_filename = datetime.now().strftime("%Y%m%d_%H%M%S") + self.video_file_name + "_原文.srt"
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "保存翻譯後的SRT文件",
            default_filename,
            "SRT Files (*.srt);;All Files (*)"
        )
        
        if file_path:
            try:
                # 使用自定義的字幕生成方法
                self.generate_srt(
                    self.subtitles,
                    file_path,
                )
                # 成功提示
                QMessageBox.information(self, "成功", f"SRT 文件已保存到: {file_path}")
            except Exception as e:
                # 錯誤提示
                QMessageBox.critical(self, "錯誤", f"文件保存失敗: {str(e)}")
                
    def translate_srt_button_click(self):
        """翻譯後的srt button 點擊"""
        if not self.translation_complete:
            QMessageBox.critical(self, "錯誤", "尚未上傳文件或開始語音轉文字")
            return
            
        default_filename = datetime.now().strftime("%Y%m%d_%H%M%S") + self.video_file_name + "_翻譯.srt"
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "保存翻譯後的SRT文件",
            default_filename,
            "SRT Files (*.srt);;All Files (*)"
        )

        if file_path:
            try:
                # 使用自定義的字幕生成方法
                self.generate_srt(
                    self.subtitles,
                    file_path,
                    text_field="chinese_text"  # 使用翻譯文本字段
                )
                # 成功提示
                QMessageBox.information(self, "成功", f"SRT 文件已保存到: {file_path}")
            except Exception as e:
                # 錯誤提示
                QMessageBox.critical(self, "錯誤", f"文件保存失敗: {str(e)}")

        
    def seek_video(self):
        """调整播放进度"""
        value = self.progress_bar.value()
        self.progress_label.setText(f"{value}%")
        self.status_label.setText(f"狀態：調整到 {value}%")

    def start_speech_to_text_processing(self):
        """启动语音转文字"""
        if not self.video_file:
            self.status_label.setText("狀態：請先選擇文件")
            return
        
        self.start_processing()
        print("video_file:" + self.video_file)
        self.status_label.setText("狀態：正在進行語音轉文字...")
        
        self.video_thread = VideoProcessThread(self.video_file, self.audio_path)
        self.video_thread.progress_signal.connect(self.update_progress)
        self.video_thread.transcribed_signal.connect(self.update_transcribed_text)
        self.video_thread.translated_signal.connect(self.update_translated_text)
        self.video_thread.all_transcribed_signal.connect(self.update_all_transcribed_text)
        self.video_thread.subtitles_signal.connect(self.update_subtitles_data)
        self.video_thread.error_signal.connect(self.show_error)
        self.video_thread.start()
        
    def show_error(self, error_message):
        """顯示錯誤訊息"""
        # 使用 QTimer 在主線程中顯示錯誤對話框
        # QTimer.singleShot(0, lambda: self._show_error_dialog(error_message))
        print(error_message)
        QMessageBox.critical(self, "錯誤",error_message)
        
    def update_progress(self, value):
        """更新進度條"""
        self.progress_bar.setValue(value)
        
    def update_processing_time(self):
            """每秒更新处理时间"""
            self.processing_seconds += 1
            self.processing_time_label.setText(f"處理秒數：{self.processing_seconds} 秒")

    def update_transcribed_text(self, text):
        """更新UI中的轉錄字幕"""
        self.transcribed_text = text
        self.speech_recognition_textEdit.setText(self.transcribed_text)

    def update_translated_text(self, text):
        """更新UI中的翻譯字幕"""
        self.translated_text = text
        self.translate_textEdit.setText(self.translated_text)

    def update_all_transcribed_text(self, text):
        """更新UI中的翻譯字幕"""
        self.all_transcribed_text = text
        self.all_speech_recognition_textEdit.setText(self.all_transcribed_text)
    
    def update_subtitles_data(self,subtitles):
        self.subtitles = subtitles
        self.translation_complete = True
        self.status_label.setText("狀態：語音轉文字完成")
        self.status_label.setStyleSheet("color: green;font-size: 14px;")
        self.finish_processing()
        
        
    def translation_click_message(self):
        if not self.translation_complete:
            QMessageBox.critical(self, "錯誤", "尚未上傳文件或開始語音轉文字")
            
    def start_processing(self):
        """开始处理"""
        self.processing_seconds = 0  # 重置秒数
        self.status_label.setText("狀態：處理中")
        self.status_label.setStyleSheet("color: orange;")  # 状态颜色为橙色
    
        self.timer.start(1000)  # 每秒触发一次
    
        # 模拟长时间处理
        # QTimer.singleShot(5000, self.finish_processing)  # 5秒后完成处理
            
    def finish_processing(self):
        """完成处理"""
        self.timer.stop()
        self.status_label.setText("狀態：處理完成")
        self.status_label.setStyleSheet("color: green;")  # 状态颜色为绿色
        self.processing_time_label.setText(f"處理完成，共耗時 {self.processing_seconds} 秒")
        QMessageBox.information(self, "完成", f"處理完成，共耗時 {self.processing_seconds} 秒")
        
    def format_time(self,seconds):
        # 将秒数转换为 SRT 的时间格式
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

        
    def generate_srt(self,subtitles, output_file,text_field="text"):
        with open(output_file, 'w', encoding='utf-8') as f:
            for idx, subtitle in enumerate(subtitles, start=1):
                # 写入序号
                f.write(f"{idx}\n")
                # 写入时间戳
                start_time = self.format_time(subtitle['start'])
                end_time = self.format_time(subtitle['end'])
                f.write(f"{start_time} --> {end_time}\n")
                # 写入字幕内容
                text = subtitle.get(text_field, "")
                f.write(f"{text}\n\n")
                
    def download_srt_file(self):
        """播放或暂停视频"""
        if not self.video_file:
            self.status_label.setText("狀態：請先選擇文件")
            return

        if self.playing:
            self.play_button.setText("播放")
            self.status_label.setText("狀態：已暂停")
            self.playing = False
        else:
            self.play_button.setText("暂停")
            self.status_label.setText("狀態：播放中")
            self.playing = True
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec())
