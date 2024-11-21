# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 17:38:16 2024

@author: peter
"""

from moviepy.editor import VideoFileClip

def extract_audio(input_video, output_audio):
    # 讀取影片
    video = VideoFileClip(input_video)
    # 提取音頻
    audio = video.audio
    # 儲存音頻為 WAV 格式
    audio.write_audiofile(output_audio, codec='pcm_s16le')

output_video = "不為誰而作的歌.mp4"
output_audio = "不為誰而作的歌.wav"
extract_audio(output_video, output_audio)

