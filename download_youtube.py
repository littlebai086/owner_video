# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 18:20:10 2024

@author: peter
"""

import yt_dlp

video_url = "https://youtube.com/watch?v=gd38-X3HpbM"

ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': './%(title)s.%(ext)s',  # 设置输出文件的名称和扩展名
    'postprocessors': [{  # 使用 postprocessor 转换格式
        'key': 'FFmpegVideoConvertor',  # 使用 FFmpeg 进行转换
        'preferedformat': 'mp4',  # 设置目标格式为 MP4
    }],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])
