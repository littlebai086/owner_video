# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 15:10:09 2024

@author: peter
"""

import ffmpeg
import os

def add_srt_subtitles(video_path, srt_path, output_path):
    """
    将 SRT 字幕嵌入到视频文件中。
    :param video_path: 原始视频文件路径
    :param srt_path: SRT 字幕文件路径
    :param output_path: 输出文件路径
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在：{video_path}")
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"SRT 字幕文件不存在：{srt_path}")
    
    try:
        # 使用 FFmpeg 的 subtitles 滤镜嵌入字幕
        (
            ffmpeg
            .input(video_path)
            .output(output_path, vf=f"subtitles={srt_path}")
            .run(overwrite_output=True)
        )
        # 這樣可以自定義字體大小和顏色。
        # vf=f"subtitles={srt_path}:force_style='Fontsize=24,PrimaryColour=&HFFFFFF&'"
        print(f"字幕嵌入成功，输出文件位于：{output_path}")
    except ffmpeg.Error as e:
        print("FFmpeg 错误：", e.stderr.decode())
        raise

# 示例调用
video_file = "不為誰而作的歌.mp4"  # 替换为实际的视频文件路径
subtitle_file = "20241223_153418不為誰而作的歌_翻譯.srt"  # 替换为实际的 SRT 字幕路径
output_file = "不為誰而作的歌_with_subtitles.mp4"  # 输出文件路径

try:
    add_srt_subtitles(video_file, subtitle_file, output_file)
except Exception as e:
    print(f"发生错误：{e}")
