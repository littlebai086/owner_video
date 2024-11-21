# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 17:17:17 2024

@author: peter
"""

from googletrans import Translator
import whisper

def translate_text(text):
    """翻譯文字為繁體中文"""
    print("翻譯文字為繁體中文")
    translator = Translator()
    return translator.translate(text, src='en', dest='zh-TW').text
# 加载模型（模型大小可以选择：tiny, base, small, medium, large）
model = whisper.load_model("base")  # 选择 'base' 模型，适合快速测试

audio_file1 = "audio_mono.wav"
audio_file1 = "chinese_test.wav"
audio_file1 = "不為誰而作的歌.wav"
audio_file1 = "audio.wav"
# 加载音频文件并进行语音识别
result = model.transcribe(audio_file1)  # 支持 MP3, WAV, FLAC 格式

# 输出结果
print("Recognized Text:")
print(result["text"])

translate_text(result["text"])
