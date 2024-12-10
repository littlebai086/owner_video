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
from PySide6.QtWidgets import (
    QApplication, QVBoxLayout, QPushButton,
    QWidget, QLabel, QHBoxLayout, QSlider, 
    QTextEdit, QFileDialog, QMessageBox,
    QProgressBar ,QComboBox, QStackedWidget
    )

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QThread, Signal,QTimer, QUrl, Slot
# from PyQt6.QtGui import QIcon
from moviepy import VideoFileClip
# from moviepy.editor import VideoFileClip
import os
import shutil
from googletrans import Translator
from datetime import datetime
import time
# from pydub.utils import mediainfo
# import whisper
from faster_whisper import WhisperModel
import torch

class CommonClass():
    
    def list_devices(self):
        """列出可用的設備 (GPU 和 CPU)。"""
        devices = []
        
        # 檢查 GPU 是否可用
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                devices.append(f"GPU:{i} ({torch.cuda.get_device_name(i)})")
        
        # 添加 CPU
        devices.append("CPU")
        return devices
    
    def list_available_devices(self):
        devices = {}
    
        # 检查 CPU
        devices["CPU"] = "Available"
    
        # 检查 XPU
        if hasattr(torch, "xpu") and torch.xpu.is_available():
            devices["XPU"] = torch.xpu.get_device_name()
        else:
            devices["XPU"] = "Not available"
    
        # 检查 GPU
        if torch.cuda.is_available():
            gpu_devices = []
            for i in range(torch.cuda.device_count()):
                gpu_devices.append(torch.cuda.get_device_name(i))
            devices["GPU"] = gpu_devices
        else:
            devices["GPU"] = "Not available"
        print(devices)
        return devices

class VideoProcessThread(QThread):
    progress_signal = Signal(int)
    error_signal = Signal(str)
    transcribed_signal = Signal(str)
    translated_signal = Signal(str)
    translated_subtitles_signal = Signal(list)
    all_transcribed_signal = Signal(str)
    subtitles_signal = Signal(list,list)

    def __init__(self, video_path, audio_path,model):
        super().__init__()
        self.video_path = video_path
        self.audio_path = audio_path
        self.model = model
        # self.subtitles = None
        # self.model = WhisperModel.load_model("small", compute_type="float16")  # 选择 'base' 模型，适合快速测试

    def run(self):
        try:
            # 擷取音訊並轉為文字
            print("擷取音訊並轉為文字")
            audio_file = self.extract_audio(self.video_path)
            transcribed_text,all_transcribed_text,subtitles,translate_text,translate_subtitles = self.transcribe_audio(audio_file)

            self.transcribed_signal.emit(transcribed_text)  # 發送轉錄文字訊號
            # self.subtitles_signal.emit(subtitles)
            self.subtitles_signal.emit(subtitles,translate_subtitles)
            self.all_transcribed_signal.emit(all_transcribed_text)  # 發送轉錄文字訊號
            
            # 翻譯文字
            print("翻譯文字")
            # print(translate_text)
            self.translated_signal.emit(translate_text)  # 發送翻譯文字訊號
            # subtitles = self.translate_text_to_subtitles(translate_subtitles,translated_text)
            # self.translated_subtitles_signal.emit(translate_subtitles)
        except Exception as e:
            self.error_signal.emit(str(e))

    def extract_audio(self, video_file):
        """从视频文件中提取音频并保存为 WAV 格式"""
        # 获取当前执行的文件目录
        current_dir = os.getcwd()
        # 提取文件名（不包括路径和扩展名）
        file_name_without_extension = os.path.splitext(os.path.basename(video_file))[0]
        # 构造输出音频文件路径，放在当前目录下
        output_audio = os.path.join(current_dir, file_name_without_extension + ".wav")
        # 复制视频文件到当前目录
        # output_video = os.path.join(current_dir, os.path.basename(video_file))
        try:
            # if output_video:
            #     if os.path.abspath(video_file) == os.path.abspath(output_video):
            #         print("源文件和目标文件相同，直接覆盖")
            #         os.remove(output_video)
            # shutil.copy(video_file, output_video)
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
            # result = self.model.transcribe(audio_path, verbose=True)  # 支持 MP3, WAV, FLAC 格式
            segments, info = self.model.transcribe(audio_path)
            # 獲取總時長（用於進度條的總值）
            total_duration = info.duration
            progress = 0  # 初始化進度
            # 估算进度
            # total_segments = len(segments)
            text = ""
            all_text = ""
            new_segments = []
            oringinal_srts = []
            for segment in segments:
                text += f"{segment.text}\r\n"
                all_text += f"Start: {segment.start}s, End: {segment.end}s, Text: {segment.text}\r\n"
                progress = int(segment.end / total_duration * 100)
                self.progress_signal.emit(progress)
                subtitle_dict = {
                    "start" : segment.start,
                    "end" : segment.end,
                    "text" : segment.text,
                }
                oringinal_srts.append(segment.text)
                new_segments.append(subtitle_dict)
                print(f"[{segment.start} -> {segment.end}] {segment.text}")
            self.progress_signal.emit(100)
            [translate_text,translate_segments] = self.subtitleToTranslateSubtittle(new_segments,oringinal_srts)
            
            # for  i, segment in enumerate(result["segments"]):
            #     text += f"{segment['text']}\r\n"
            #     all_text += f"Start: {segment['start']}s, End: {segment['end']}s, Text: {segment['text']}\r\n"
            #     progress = int((i + 1) / total_segments * 100)
            #     self.progress_signal.emit(progress)  # 发送信号更新进度条
            #     # time.sleep(0.1)  # 模拟处理时间
            #     print(f"Start: {segment['start']}s, End: {segment['end']}s, Text: {segment['text']}")
            print("開始轉錄...")
            return [text,all_text,new_segments,translate_text,translate_segments]
        except Exception as e:
            print(f"讀取音訊時出錯: {e}")
            return [None,None,None]
        
    def subtitleToTranslateSubtittle(self,segments,oringinal_srts):
        new_translated_srt = []
        translated_all_output = ""
        for i in range(0, len(oringinal_srts), 300):  # 每次处理3行（编号、时间戳、字幕）
            part_srts = oringinal_srts[i:i+300]  # 获取当前字幕的3行（编号、时间、字幕文本）
            merged_subtitles = '\n\n'.join(part_srts)
            translated_output = self.translate_text(merged_subtitles)
            
            new_part_srts = translated_output.split('\n\n')
            new_translated_srt[i:i+300] = new_part_srts            
        print(len(segments))
        print(len(new_translated_srt))
        # print(new_translated_srt)
        for i, segment in enumerate(segments):
            segments[i]["text"] = new_translated_srt[i]
            translated_all_output += new_translated_srt[i]+"\n"
        
        return [translated_all_output,segments]
        
    def translate_text(self, text):
        """翻譯文字為繁體中文"""
        if not text or not isinstance(text, str):
            # 確保輸入為非空字串
            return text
        translator = Translator()
        
        try:
            # detected = translator.detect(text) # 自动检测语言
            # print(detected)
            translated = translator.translate(text,dest='zh-TW')
            # 確保返回的物件有 text 屬性
            if translated is None:
                print("翻譯失敗: 翻譯結果為 None")
                return text
            if hasattr(translated, 'text'):
                return translated.text
        except Exception as e:
            print(f"翻譯失敗: {e}")
        
        # 如果翻譯失敗，返回原始文本
        return text
    
    # def translate_text_to_subtitles(self,subtitles,chinese_text):
    #     chinese_translate_text_array = chinese_text.split("\r\n")
    #     for index, subtitle in enumerate(subtitles):
    #         subtitles[index]["chinese_text"] = chinese_translate_text_array[index]
    #     return subtitles

    
class SettingSelectionPage(QWidget):
    def __init__(self, switch_to_main_ui):
        super().__init__()
        self.Common_class = CommonClass()
        # self.list_devices = self.Common_class.list_devices()
        self.device_dict = self.Common_class.list_available_devices()
        self.initUI()
        self.switch_to_main_ui = switch_to_main_ui
        
    def initUI(self):
        self.setWindowTitle("設定選擇頁面")
        self.setGeometry(100, 100, 600, 300)
    
        # 主布局
        layout = QVBoxLayout()
    
        
        # 創建選擇裝置 label
        self.device_label = QLabel("請選擇裝置")
        self.device_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.device_label)
    
       # 創建裝置下拉選單 select
        self.decive_combo_box = QComboBox(self)
        self.selectDevicesItem(self.device_dict)
        for display_name, device_value in self.device_items:
            self.decive_combo_box.addItem(display_name, device_value)
        layout.addWidget(self.decive_combo_box)
    
    
        # 创建按钮来获取选择的值并进入下一页
        self.select_main_button = QPushButton("進入主界面", self)
        self.select_main_button.clicked.connect(self.into_main_ui)
        layout.addWidget(self.select_main_button)
        # 设置主布局
        self.setLayout(layout)
        
    def selectDevicesItem(self,device_dict):
       self.device_items = []
       for device_type, status in device_dict.items():
           if isinstance(status, list):  # 处理多个 GPU 的情况
               for i, gpu_name in enumerate(status):
                   display_name = f"{device_type} {i}: {gpu_name}"
                   device_value = f"cuda:{i}"  # 对应设备值
                   self.device_items.append((display_name, device_value))
           else:
               display_name = f"{device_type}: {status}"
               device_value = device_type.lower() if status != "Not available" else "none"
               self.device_items.append((display_name, device_value))
    
    def into_main_ui(self):
        """获取选择的设备并进入主界面"""    
        selected_device_value = self.decive_combo_box.currentData()
        selected_device_text = self.decive_combo_box.currentText()
        print(f"选择的设备: {selected_device_value}")
        print(f"选择的设备: {selected_device_text}")
        # 切换到主界面
        self.switch_to_main_ui(selected_device_value,selected_device_text)
       

class MainUIPage(QWidget):
    def __init__(self, selected_device_value,selected_device_text, switch_to_setting_selection):
        super().__init__()
        self.speech_recognition_text=""
        self.translate_text=""
        self.all_speech_recognition_text=""
        self.audio_path = "audio.wav"
        self.processing_seconds = 0
        # 翻譯是否完成
        self.translation_complete = False
        self.Common_class = CommonClass()
        self.selected_device_value = selected_device_value
        self.selected_device_text = selected_device_text
        self.initUI()
        self.switch_to_setting_selection = switch_to_setting_selection
        # model_path = "D:/python/modal/ggml-small.bin"
        # print(os.path.exists(model_path))
        if selected_device_value=="cpu":
            self.model = WhisperModel('turbo', device=self.selected_device_value)
        else:
            self.model = WhisperModel('base', device="cuda", compute_type="float16")
        
    def initUI(self):
        self.setWindowTitle("視頻語音轉文字工具")
        self.setGeometry(100, 100, 600, 1000)

        # 主布局
        layout = QVBoxLayout()
        
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
        self.video_widget = QVideoWidget(self)
        self.video_widget.setFixedSize(600, 300)
        # self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)
        layout.addWidget(self.video_widget)
        
        # 进度条
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setEnabled(False)
        self.slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.slider)
        
        # 時間秒數的那一行
        video_formatted_time_layout = QHBoxLayout()
        # 時間bar秒數
        self.video_formatted_time_label = QLabel("影片時間 00:00:00")
        self.video_formatted_time_label.setStyleSheet("color: blue; font-size: 14px;")
        video_formatted_time_layout.addWidget(self.video_formatted_time_label)
        
        # 時間bar總時數
        self.total_video_formatted_time_label = QLabel("影片總長度 00:00:00")
        self.total_video_formatted_time_label.setStyleSheet("color: blue; font-size: 14px;")
        video_formatted_time_layout.addWidget(self.total_video_formatted_time_label)
        
        layout.addLayout(video_formatted_time_layout)
        # 文件选择部分
        file_layout = QHBoxLayout()
        self.file_label = QLabel("未選擇文件")
        self.file_label.setStyleSheet("color: gray; font-size: 14px;")
        
        # 選擇影片按鈕
        self.select_file_button = QPushButton("選擇影片")
        self.select_file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_file_button)
        layout.addLayout(file_layout)
        
        # 創建選擇裝置 label
        self.device_label = QLabel(f"當前選擇的設備 Faster Whisper : {self.selected_device_text}")
        self.device_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.device_label)

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
                text-align: center; /* 文本水平居中 */
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
        
        # 返回按钮
        self.back_button = QPushButton("返回設備選擇", self)
        self.back_button.clicked.connect(self.on_back_button_clicked)
        layout.addWidget(self.back_button)
        # 设置主布局
        self.setLayout(layout)

        # 初始化其他属性
        self.video_file = None
        self.video_file_name = None
        self.playing = False
        # 信号绑定
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.playbackStateChanged.connect(self.play_pause)
        self.media_player.errorChanged.connect(self.on_error)
    
    def on_error(self):
        print(f"播放错误: {self.media_player.errorString()}")
        
    def on_back_button_clicked(self):
        """点击返回按钮时切换回设备选择界面"""
        self.switch_to_setting_selection()
        
    def select_file(self):
        """选择视频文件"""
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "選擇視頻文件", "", "視頻文件 (*.mp4 *.avi *.mkv *.mov)"
        )
        if file_path:
            normalized_path = os.path.normpath(file_path)
            file_url = QUrl.fromLocalFile(normalized_path)  # 转换为 QUrl 对象
            # url = file_dialog.selectedUrls()[0]
            self.video_file = normalized_path
            self.video_file_name = os.path.splitext(os.path.basename(normalized_path))[0]
            self.media_player.setSource(file_url)  
            self.slider.setEnabled(True)
            self.file_label.setText(f"已選擇文件：{file_path.split('/')[-1]}")
            self.progress_bar.setValue(0)
            self.status_label.setText("狀態：文件已加载")
            self.media_player.play()
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
            self.media_player.pause()
            self.playing = False
        else:
            self.play_button.setText("暂停")
            self.status_label.setText("狀態：播放中")
            self.media_player.play()
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
                    self.translate_subtitles,
                    file_path
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
        
        self.video_thread = VideoProcessThread(self.video_file, self.audio_path,self.model)
        self.video_thread.progress_signal.connect(self.update_progress)
        self.video_thread.transcribed_signal.connect(self.update_transcribed_text)
        self.video_thread.translated_signal.connect(self.update_translated_text)
        self.video_thread.all_transcribed_signal.connect(self.update_all_transcribed_text)
        self.video_thread.subtitles_signal.connect(self.update_subtitles_data)
        # self.video_thread.translated_subtitles_signal(self.)
        self.video_thread.error_signal.connect(self.show_error)
        self.video_thread.start()
        
    def show_error(self, error_message):
        """顯示錯誤訊息"""
        # 使用 QTimer 在主線程中顯示錯誤對話框
        # QTimer.singleShot(0, lambda: self._show_error_dialog(error_message))
        print(error_message)
        QMessageBox.critical(self, "錯誤",error_message)
        
    @Slot()
    def set_position(self, position):
        """设置播放位置"""
        print(position)
        self.media_player.pause()
        self.media_player.setPosition(position)
        self.media_player.play()
        
    @Slot()
    def update_position(self, position):
        """更新进度条位置"""
        self.slider.setValue(position)
        [hours,minutes,remaining_seconds] = self.video_formatted_time(position)
        formatted_time = f"影片時間 {hours:02}:{minutes:02}:{remaining_seconds:02}"
        self.video_formatted_time_label.setText(formatted_time)
        
    @Slot()
    def update_duration(self, duration):
        """设置进度条最大值"""
        self.slider.setRange(0, duration)
        print(duration)
        [hours,minutes,remaining_seconds] = self.video_formatted_time(duration)
        formatted_time = f"影片總長度 {hours:02}:{minutes:02}:{remaining_seconds:02}"
        self.total_video_formatted_time_label.setText(formatted_time)

        
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
    
    def update_subtitles_data(self,subtitles,translate_subtitles):
        self.subtitles = subtitles
        self.translate_subtitles = translate_subtitles
        self.translation_complete = True
        self.status_label.setText("狀態：語音轉文字完成")
        self.status_label.setStyleSheet("color: green;font-size: 14px;")
        self.finish_processing()
        
        
    def translation_click_message(self):
        if not self.translation_complete:
            QMessageBox.critical(self, "錯誤", "尚未上傳文件或開始語音轉文字")
            
    def start_processing(self):
        """开始处理"""
        self.progress_bar.setValue(0)
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

        
    def video_formatted_time(self,number,is_duration=False):
        if is_duration:
            seconds = number
        else:
            seconds = number / 1000  # 转换为秒
        minutes = int(seconds // 60)  # 获取分钟
        hours = int(minutes // 60)  # 获取分钟
        remaining_seconds = int(seconds % 60)  # 获取剩余的秒
        return [hours,minutes,remaining_seconds]
        
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
            self.media_player.pause()
            self.playing = False
        else:
            self.play_button.setText("暂停")
            self.status_label.setText("狀態：播放中")
            self.media_player.play()
            self.playing = True
          
class VideoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("設定選擇頁面")
        self.setGeometry(100, 100, 600, 300)
        # 创建 QStackedWidget 来管理页面切换
        self.stacked_widget = QStackedWidget(self)

        # 创建页面
        self.setting_selection_page = SettingSelectionPage(self.switch_to_main_ui)
        self.main_ui_page = None  # 初始化主界面为空

        # 将页面添加到 QStackedWidget
        self.stacked_widget.addWidget(self.setting_selection_page)
        
        # 设置布局
        layout = QHBoxLayout(self)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def switch_to_main_ui(self, selected_device_value,selected_device_text):
        """切换到主界面"""
        # 创建主界面并切换
        self.main_ui_page = MainUIPage(selected_device_value,selected_device_text, self.switch_to_setting_selection)
        self.stacked_widget.addWidget(self.main_ui_page)
        self.stacked_widget.setCurrentWidget(self.main_ui_page)  # 显示主界面

    def switch_to_setting_selection(self):
        """切换回设备选择页面"""
        self.stacked_widget.setCurrentWidget(self.setting_selection_page) 
          
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec())
