# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 16:25:31 2024

@author: peter
"""

from googletrans import Translator
from pydub import AudioSegment
from moviepy.editor import VideoFileClip

def clip_video(input_video, start_time, end_time, output_video):
    # 讀取影片
    video = VideoFileClip(input_video)
    # 剪輯影片，從 start_time 開始
    clipped_video = video.subclip(start_time, end_time)
    # 儲存剪輯後的影片
    clipped_video.write_videofile(output_video, codec='libx264')
    
def extract_audio(input_video, output_audio):
    # 讀取影片
    video = VideoFileClip(input_video)
    # 提取音頻
    audio = video.audio
    # 儲存音頻為 WAV 格式
    audio.write_audiofile(output_audio, codec='pcm_s16le')
# 範例：將影片從 1 分 30 秒開始剪輯
input_video = "See_You_Again.mp4"
start_time = (1, 30)  # 分鐘:秒
end_time = (2, 0)     # 3 分 00 秒
output_video = "See_You_Again_Part.mp4"
clip_video(input_video, start_time, end_time, output_video)


output_audio = "See_You_Again_Part.wav"
extract_audio(output_video, output_audio)
def translate_text(text):
    """翻譯文字為繁體中文"""
    print("翻譯文字為繁體中文")
    translator = Translator()
    return translator.translate(text, src='en', dest='zh-TW').text
# 加载音频文件
audio = AudioSegment.from_wav("audio.wav")

# 剪切从 10 秒到 20 秒之间的部分（单位为毫秒）
start_time = 10 * 1000  # 10秒 = 10 * 1000 毫秒
end_time = 20 * 1000  # 20秒 = 20 * 1000 毫秒

# 剪切音频
extracted_audio = audio[start_time:end_time]

# 导出剪辑后的音频
extracted_audio.export("extracted_audio.wav", format="wav")

print("音频剪辑完成，文件已保存为 'extracted_audio.wav'")

import speech_recognition as sr

recognizer = sr.Recognizer()

# 確保檔案存在且格式正確
file_path = "extracted_audio.wav"
file_path = "audio_part.wav"
try:
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language='en-US')
        text = recognizer.recognize_google(audio_data, language='en-US')
        print("識別結果:", text)
    except sr.UnknownValueError:
        print("Google 語音識別無法理解音訊")
    except sr.RequestError as e:
        print(f"無法連接到語音識別服務; 請檢查網絡或 API 配置: {e}")
        print("音訊成功讀取！")
except Exception as e:
    print(f"讀取音訊時出錯: {e}")
    
translate_text(text)
