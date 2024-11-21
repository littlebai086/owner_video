# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 10:10:15 2024

@author: peter
"""

from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import wave
import json

model_path = "F:\\python_model\\vosk-model-en-us-0.22"  # 修改為你的模型路徑

try:
    model = Model(model_path)
    print("Model loaded successfully")
except Exception as e:
    print(f"Failed to load model: {e}")

audio_file = "audio.wav"
audio_file = "See_You_Again_Part.wav"
audio_file1 = "audio_mono.wav"
# 將音頻轉換為單聲道
audio = AudioSegment.from_wav(audio_file)
audio = audio.set_channels(1)
audio.export(audio_file1, format="wav")

with wave.open(audio_file1, "rb") as wf:
    sample_rate = wf.getframerate()  # 採樣率（Hz）
    channels = wf.getnchannels()    # 聲道數
    sampwidth = wf.getsampwidth()   # 每樣本的位元數（字節）
    frames = wf.getnframes()        # 總幀數
    duration = frames / sample_rate  # 總時長（秒）
    recognizer = KaldiRecognizer(model, sample_rate)
    print(f"採樣率: {sample_rate / 1000:.1f} kHz")
    print(f"聲道數: {channels}")
    print(f"每樣本位元數: {sampwidth * 8} bits")
    print(f"音檔總時長: {duration:.2f} 秒")
    audio_data = wf.readframes(wf.getnframes())
    if recognizer.AcceptWaveform(audio_data):
        result_json = recognizer.Result()
        result = json.loads(result_json)
        print(f"Recognized Text: {result.get('text', '')}")
    else:
        partial_result_json = recognizer.FinalResult()
        partial_result = json.loads(partial_result_json)
        print(f"Final Recognized Text: {partial_result.get('text', '')}")
    # while True:
    #     data = wf.readframes(4000)  # 每次讀取 4000 幀
    #     if len(data) == 0:
    #         break  # 結束時退出
        
    #     if recognizer.AcceptWaveform(data):
    #         result_json = recognizer.Result()
    #         result = json.loads(result_json)
    #         print(f"Partial Recognized Text: {result.get('text', '')}")

    # # 處理未完成部分
    # final_result_json = recognizer.FinalResult()
    # final_result = json.loads(final_result_json)
    # print(f"Final Recognized Text: {final_result.get('text', '')}")
    # 處理未完成的部分（可能是音頻最後的小段）
    # partial_result_json = recognizer.FinalResult()
    # partial_result = json.loads(partial_result_json)
    # print(f"Final Recognized Text: {partial_result.get('text', '')}")