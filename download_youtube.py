# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 18:20:10 2024

@author: peter
"""

import yt_dlp

video_url = "https://youtube.com/watch?v=gd38-X3HpbM"

ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': './%(title)s.%(ext)s'
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])